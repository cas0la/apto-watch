"""VivaReal e ZAP (mesmo grupo, mesmo HTML e mesmos códigos de anúncio).

Lista: cards `[data-cy="rp-property-cd"]` já vêm no HTML do servidor.
Detalhe: endereço, condomínio, IPTU, comodidades, descrição, fotos e coordenadas.
"""
from __future__ import annotations

import math
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from bs4 import BeautifulSoup

PAGE_SIZE = 30
PHOTO_URL = "https://resizedimgs.vivareal.com/img/vr-listing/{h}/f.webp?action=fit-in&dimension=800x600"


def _int(s) -> int | None:
    d = re.sub(r"\D", "", s or "")
    return int(d) if d else None


def page_url(url: str, page: int) -> str:
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "pagina"]
    if page > 1:
        q.append(("pagina", str(page)))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q, safe=","), ""))


def total_pages(html: str) -> int | None:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    n = _int((h1.get_text(" ") if h1 else "").split(" ")[0])
    return math.ceil(n / PAGE_SIZE) if n else None


def parse_list(html: str, source: str = "vivareal") -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for card in soup.select('[data-cy="rp-property-cd"]'):
        a = card.find("a", href=True)
        m = re.search(r"-id-(\d{6,})", a["href"]) if a else None
        if not m:
            continue

        def txt(cy):
            el = card.select_one(f'[data-cy="{cy}"]')
            return el.get_text(" ", strip=True) if el else ""

        price = txt("rp-cardProperty-price-txt")
        rent = re.search(r"R\$\s*([\d.]+)\s*/\s*m[êe]s", price)
        cond = re.search(r"Cond\.\s*R\$\s*([\d.]+)", price)
        iptu = re.search(r"IPTU\s*R\$\s*([\d.]+)", price)
        loc = txt("rp-cardProperty-location-txt")
        bairro, _, cidade = loc.rpartition(",")
        img = card.find("img", src=re.compile("resizedimgs"))
        h = re.search(r"vr-listing/([a-f0-9]{32})/", img["src"]) if img else None
        out.append({
            "id": m.group(1),
            "source": source,
            "url": a["href"].split("?")[0],
            "title": txt("card-property-content")[:200] or None,
            "rent": _int(rent.group(1)) if rent else None,
            "cond": _int(cond.group(1)) if cond else 0,
            "iptu": f"R$ {iptu.group(1)}" if iptu else None,
            "area": _int(txt("rp-cardProperty-propertyArea-txt")),
            "quartos": _int(txt("rp-cardProperty-bedroomQuantity-txt")),
            "banheiros": _int(txt("rp-cardProperty-bathroomQuantity-txt")),
            "vagas": _int(txt("rp-cardProperty-parkingSpacesQuantity-txt")),
            "bairro": bairro.strip() or None,
            "cidade": cidade.strip() or loc.strip() or None,
            "street": txt("rp-cardProperty-street-txt") or None,
            "photos": [PHOTO_URL.format(h=h.group(1))] if h else [],
        })
    return out


def detail_url(listing_id: str) -> str:
    # O site resolve o anúncio pelo código no fim da URL; o texto antes dele é ignorado.
    # Formato testado em 06/11/2026. ZAP usa os mesmos códigos, então o detalhe vem sempre do VivaReal.
    return f"https://www.vivareal.com.br/imovel/apartamento-2-quartos-sao-jose-com-garagem-id-{listing_id}/"


def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    def tid(name):
        el = soup.select_one(f'[data-testid="{name}"]')
        return el.get_text(" ", strip=True) if el else ""

    raw = html.replace('\\"', '"')
    out: dict = {}
    if tid("location-address"):
        out["addr"] = tid("location-address")
    cond = _int(tid("condoFee"))
    if cond is not None:
        out["cond"] = cond
    m = re.search(r'"monthly":\{[^}]*?"price":(\d+)', raw)
    if m:
        out["rent"] = int(m.group(1))
    iptu = tid("iptu")
    if iptu and "não" not in iptu.lower():
        out["iptu"] = iptu.split("/")[0].strip()
    am = soup.select_one('[data-testid="amenities-list"]')
    if am:
        out["amenities"] = [c.get_text(" ", strip=True) for c in am.find_all(recursive=False) if c.get_text(strip=True)]
        out["amenities"] = [x for x in out["amenities"] if not re.fullmatch(r"0 suítes?", x)]
    desc = soup.select_one('[data-testid="description-content"]')
    if desc:
        out["descricao"] = desc.get_text("\n", strip=True)[:4000]
    i = re.search(r'"images":\[', raw)
    if i:
        seg = raw[i.end(): raw.find("]", i.end())]
        hashes = list(dict.fromkeys(re.findall(r"vr-listing/([a-f0-9]{32})/", seg)))
        if hashes:
            out["photos"] = [PHOTO_URL.format(h=h) for h in hashes]
    g = re.search(r"maps/embed/v1/place[^\"']*?q=(-?[\d.]+)%2C(-?[\d.]+)", html)
    if g:
        out["lat"], out["lon"] = float(g.group(1)), float(g.group(2))
    return out
