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
    for campo, chave in (("quartos", "min_quartos"), ("banheiros", "min_banheiros"), ("vagas", "min_vagas")):
        if a.get(chave) and (l.get(campo) or 0) < a[chave]:
            return False
    if a.get("exigir_pet") and l.get("pet") != "SIM":
        return False
    return True
