"""ISCI Imóveis (isciimoveis.com.br), imobiliária de Palhoça. O site roda sobre o Imoview.

A página de busca monta os cards por JavaScript com um POST para /retornar-imoveis-disponiveis,
que devolve JSON (20 anúncios por página). O endereço vem mascarado ("*****"); bairro, cidade,
valores, quartos, banheiros, vagas e fotos vêm abertos. A descrição e as características ficam
na página de detalhe (/imovel/<url_amigavel>/<codigo>), em HTML. Formato observado em 16/11/2026.

A URL da busca no config.yaml guarda os filtros na query, por exemplo:
https://www.isciimoveis.com.br/aluguel/apartamento?banheiros=2&vagas=1
"""
from __future__ import annotations

import json
import math
import re
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

BASE = "https://www.isciimoveis.com.br"
ENDPOINT = f"{BASE}/retornar-imoveis-disponiveis"
PAGE_SIZE = 20
TIPOS = {"apartamento": (2, "Apartamento")}


def _money(s) -> int | None:
    m = re.search(r"R\$\s*([\d.]+)(?:,\d{2})?", s or "")
    return int(m.group(1).replace(".", "")) if m else None


def _int(s) -> int | None:
    d = re.sub(r"\D", "", str(s or ""))
    return int(d) if d else None


def _area(s) -> int | None:
    m = re.match(r"\s*([\d.]+)(?:,(\d+))?", str(s or ""))
    if not m:
        return None
    v = round(float(m.group(1).replace(".", "") + "." + (m.group(2) or "0")))
    return v or None


def payload(url: str, page: int) -> dict:
    """Corpo do POST no formato que o jQuery da página envia ($.param do objeto `imovel`)."""
    p = urlsplit(url)
    q = {k: v[0] for k, v in parse_qs(p.query).items()}
    slug = p.path.rstrip("/").split("/")[-1]
    tipo = TIPOS.get(slug)
    data = {
        "finalidade": "aluguel", "codigounidade": "", "codigocondominio": 0, "codigoproprietario": 0,
        "codigocaptador": 0, "codigosimovei": 0, "codigocidade": 0, "codigoregiao": 0, "endereco": "",
        "edificio": "", "numeroquartos": q.get("quartos", 0), "numerovagas": q.get("vagas", 0),
        "numerobanhos": q.get("banheiros", 0), "numerosuite": 0, "numerovaranda": 0, "numeroelevador": 0,
        "valorde": 0, "valorate": 0, "areade": 0, "areaate": 0, "areaexternade": 0, "areaexternaate": 0,
        "extras": "", "destaque": 0, "opcaoimovel[codigo]": 0, "opcaoimovel[nome]": "",
        "opcaoimovel[nomeUrl]": "todas-as-opcoes", "codigoOpcaoimovel": 0, "numeropagina": page,
        "numeroregistros": PAGE_SIZE, "ordenacao": "dataatualizacaodesc", "condominio[codigo]": 0,
        "condominio[nome]": "", "condominio[nomeUrl]": "todos-os-condominios",
    }
    if tipo:
        data.update({"tipos[0][codigo]": tipo[0], "tipos[0][nome]": tipo[1], "tipos[0][url_amigavel]": slug})
    return data


def fetch_page(client, url: str, page: int) -> str:
    return client.post(ENDPOINT, payload(url, page))


def _data(text: str) -> dict:
    d = json.loads(text)
    if d.get("error"):  # o site devolve {"error": true, "redirect": ".../manutencao"} quando o backend falha
        raise ValueError(f"Isci recusou a busca: {d.get('message') or d.get('log')}")
    return d


def total_pages(text: str) -> int | None:
    q = _data(text).get("quantidade")
    return max(1, math.ceil(int(q) / PAGE_SIZE)) if q is not None else None


def parse_list(text: str, source: str = "isci") -> list[dict]:
    out = []
    for h in _data(text).get("lista") or []:
        if str(h.get("finalidade", "")).lower() != "aluguel":
            continue
        cod = h["codigo"]
        photos = [f["urlp"] for f in h.get("fotos") or [] if f.get("urlp")] or [h.get("urlfotoprincipalp")]
        out.append({
            "id": f"isci-{cod}",
            "source": source,
            "url": f"{BASE}/imovel/{h.get('url_amigavel') or 'imovel'}/{cod}",
            "title": h.get("titulo"),
            "street": None,  # o site mascara rua e número
            "bairro": h.get("bairro") or None,
            "cidade": h.get("cidade") or None,
            "rent": _money(h.get("valor")),
            "cond": _money(h.get("valorcondominio")) or 0,
            "area": _area(h.get("areaprincipal")),
            "quartos": _int(h.get("numeroquartos")),
            "banheiros": _int(h.get("numerobanhos")),
            "vagas": _int(h.get("numerovagas")),
            "photos": [p.split("?")[0] for p in photos if p][:30],
        })
    return out


def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    desc = soup.select_one(".descricao")
    text = re.sub(r"\s+", " ", soup.get_text(" "))
    iptu = re.search(r"IPTU\s*(R\$\s*[\d.]+(?:,\d{2})?)", text)
    am = [re.sub(r"\s+", " ", li.get_text(" ", strip=True)) for li in soup.select(".lista-caracteristicas-extras .extras-active")]
    return {
        "descricao": desc.get_text(" ", strip=True) if desc else None,
        "amenities": list(dict.fromkeys(a for a in am if a)),
        "iptu": iptu.group(1).replace(",00", "") if iptu else None,
    }
