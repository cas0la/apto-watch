"""Regras de entrada na lista e de disparo de alertas."""
from __future__ import annotations

import re
import unicodedata

PET_NEG = re.compile(
    r"\b(n[ãa]o|proibid\w*|vedad\w*|sem)\b[^.;\n]{0,40}\b(animal|animais|pets?|cachorros?|c[ãa]es|gatos?)\b"
    r"|\b(animal|animais|pets?)\b[^.;\n]{0,30}\b(n[ãa]o (s[ãa]o )?(aceit|permit)\w*|proibid\w*|vedad\w*)",
    re.I,
)
PET_POS = re.compile(r"aceita animais|aceita pets?|permite pets?|pet.?friendly|(aceita|permite)[^.]{0,20}(pet|animais)", re.I)

REGIAO_DE_CIDADE = {"palhoca": "Pedra Branca (Palhoça)", "sao jose": "São José", "florianopolis": "Florianópolis"}


def norm(s: str | None) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def regiao(cidade: str | None) -> str | None:
    return REGIAO_DE_CIDADE.get(norm(cidade))


def pet_status(text: str) -> tuple[str, str | None]:
    """('NAO', trecho) se o texto diz que não aceita; ('SIM', None) se diz que aceita; senão ('?', None)."""
    m = PET_NEG.search(text or "")
    if m:
        a = max(0, m.start() - 40)
        return "NAO", (text[a : m.end() + 30]).strip()
    if PET_POS.search(text or ""):
        return "SIM", None
    return "?", None


def bairro_ok(cidade: str | None, bairro: str | None, regras: dict) -> bool:
    regra = None
    for nome, r in regras.items():
        if norm(nome) == norm(cidade):
            regra = r or {}
    if regra is None:
        return False
    b = norm(bairro)
    incluir = [norm(x) for x in regra.get("incluir", [])]
    excluir = [norm(x) for x in regra.get("excluir", [])]
    if incluir and not any(_has(b, x) for x in incluir):
        return False
    if any(_has(b, x) for x in excluir):
        return False
    return True


def _has(bairro: str, nome: str) -> bool:
    """'cidade universitaria pedra branca' contém 'pedra branca'; compara palavras inteiras."""
    return bool(nome) and re.search(rf"(^|\s){re.escape(nome)}(\s|$)", bairro) is not None


def base_ok(l: dict, crit: dict) -> tuple[bool, str]:
    """O anúncio entra na lista? Devolve (ok, motivo)."""
    total = (l.get("rent") or 0) + (l.get("cond") or 0)
    if not l.get("rent"):
        return False, "sem preço"
    if total > crit.get("max_total", 10**9):
        return False, f"total {total}"
    if (l.get("banheiros") or 0) < crit.get("min_banheiros", 0):
        return False, "banheiros"
    if (l.get("vagas") or 0) < crit.get("min_vagas", 0):
        return False, "vagas"
    if not bairro_ok(l.get("cidade"), l.get("bairro"), crit.get("regioes", {})):
        return False, f"bairro {l.get('bairro')}/{l.get('cidade')}"
    if l.get("pet") == "NAO":
        return False, "não aceita pet"
    return True, ""


def alert_match(l: dict, a: dict) -> bool:
    total = (l.get("rent") or 0) + (l.get("cond") or 0)
    if a.get("max_total") and total > a["max_total"]:
        return False
    if a.get("regioes") and l.get("regiao") not in a["regioes"]:
        return False
    b = norm(l.get("bairro"))
    inc = [norm(x) for x in a.get("bairros_incluir") or [] if x.strip()]
    exc = [norm(x) for x in a.get("bairros_excluir") or [] if x.strip()]
    if inc and not any(_has(b, x) for x in inc):
        return False
    if any(_has(b, x) for x in exc):
        return False
    for campo, chave in (("quartos", "min_quartos"), ("vagas", "min_vagas")):
        if a.get(chave) and (l.get(campo) or 0) < a[chave]:
            return False
    # 1 banheiro fica na aba própria: só avisa quando o alerta pede 1 banheiro de propósito.
    if (l.get("banheiros") or 0) < (a.get("min_banheiros") or 2):
        return False
    if a.get("exigir_pet") and l.get("pet") != "SIM":
        return False
    return True


def anunciante(nome: str | None) -> str | None:
    """Nome da imobiliária sem filial nem razão social: 'Ibagy Imóveis - Kobrasol' -> 'Ibagy Imóveis'."""
    n = re.sub(r"\s+", " ", nome or "").strip()
    if not n:
        return None
    n = re.split(r"\s+[-–|]\s+", n)[0]
    n = re.sub(r"[\s,.]+(ltda|ltda\.|eireli|me|epp|s/?a|creci.*)$", "", n, flags=re.I).strip(" .,-")
    return n or None


BANHEIROS_PRESUMIDOS = {"ibagy"}
_TIPO_RUA = re.compile(r"^(rua|r|avenida|av|travessa|tv|servidao|serv|rodovia|rod|estrada|alameda|al)\b\.?\s*")


def rua(l: dict) -> tuple[str, frozenset] | None:
    """(nome da rua, números) quando o anúncio traz rua de verdade; None quando só tem bairro/cidade."""
    s = norm(l.get("street") or "")
    if not s or s.startswith("endereco nao informado"):
        return None
    b, c = norm(l.get("bairro")), norm(l.get("cidade"))
    if (b and s.startswith(b)) or (c and s.startswith(c)):
        return None
    nums = frozenset(re.findall(r"\b\d{1,5}\b", s))  # "Luiz Fagundes, 980, 2270": número e complemento
    nome = re.sub(r"[^a-z ]", " ", _TIPO_RUA.sub("", s))
    nome = re.sub(r"\s+", " ", nome).strip()
    return (nome, nums) if nome else None


def mesmo_imovel(a: dict, b: dict) -> bool:
    """Dois anúncios do mesmo apartamento (outro site, ou outra imobiliária no mesmo portal).

    - Mesma cidade, área a até 3 m² (as duas informadas), quartos e banheiros iguais quando os dois dizem.
    - Com rua nos dois: mesmo nome de rua e número igual quando os dois têm número.
      Sites diferentes: total a até R$ 150 (o condomínio costuma vir arredondado num deles).
      Mesmo site: só com número nos dois e total a até R$ 30 (podem ser apartamentos do mesmo prédio).
    - Sem rua num dos lados: só entre sites diferentes, mesmo bairro e total a até R$ 10.
    """
    if norm(a.get("cidade")) != norm(b.get("cidade")):
        return False
    if not a.get("area") or not b.get("area") or abs(a["area"] - b["area"]) > 3:
        return False
    if a.get("quartos") and b.get("quartos") and a["quartos"] != b["quartos"]:
        return False
    # A Ibagy não informa banheiros (o número vem do filtro da busca): só compara quando os dois sites dizem.
    if a.get("source") not in BANHEIROS_PRESUMIDOS and b.get("source") not in BANHEIROS_PRESUMIDOS \
            and a.get("banheiros") and b.get("banheiros") and a["banheiros"] != b["banheiros"]:
        return False
    d = abs(((a.get("rent") or 0) + (a.get("cond") or 0) if a.get("total") is None else a["total"])
            - ((b.get("rent") or 0) + (b.get("cond") or 0) if b.get("total") is None else b["total"]))
    mesmo_site = a.get("source") == b.get("source")
    ra, rb = rua(a), rua(b)
    if ra and rb:
        if ra[0] != rb[0] or (ra[1] and rb[1] and not ra[1] & rb[1]):
            return False
        if mesmo_site:
            return bool(ra[1] and rb[1]) and d <= 30
        return d <= 150
    if mesmo_site:
        return False
    ba, bb = norm(a.get("bairro")), norm(b.get("bairro"))
    return bool(ba and bb) and (ba == bb or _has(ba, bb) or _has(bb, ba)) and d <= 10
