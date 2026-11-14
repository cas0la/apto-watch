"""QuintoAndar: a primeira página da busca vem no __NEXT_DATA__ (initialState.houses)."""
from __future__ import annotations

import json

from bs4 import BeautifulSoup

LABELS = {"AREA_DE_SERVICO": "Área de serviço", "PISCINA": "Piscina", "ACADEMIA": "Academia",
          "SALAO_DE_FESTAS": "Salão de festas", "PLAYGROUND": "Playground", "ELEVADOR": "Elevador",
          "ACEITA_PET": "Aceita animais", "CHURRASQUEIRA": "Churrasqueira", "VARANDA": "Varanda",
          "AR_CONDICIONADO": "Ar-condicionado", "AQUECIMENTO_A_GAS": "Aquecimento a gás", "GAS_ENCANADO": "Gás encanado"}


def page_url(url: str, page: int) -> str:
    return url  # só a primeira página vem no HTML; as demais exigem a API interna


def parse_list(html: str, source: str = "quintoandar") -> list[dict]:
    tag = BeautifulSoup(html, "lxml").find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return []
    houses = (json.loads(tag.string).get("props", {}).get("pageProps", {})
              .get("initialState", {}).get("houses", {})) or {}
    out = []
    for h in houses.values():
        if not isinstance(h, dict) or "id" not in h:
            continue
        if not h.get("forRent") and not h.get("rentPrice"):
            continue
        addr = h.get("address") or {}
        tags = (h.get("amenities") or []) + (h.get("installations") or [])
        am = [LABELS.get(t, t.replace("_", " ").capitalize()) for t in tags]
        if h.get("isFurnished"):
            am.append("Mobiliado")
        out.append({
            "id": f"qa-{h['id']}",
            "source": source,
            "url": f"https://www.quintoandar.com.br/imovel/{h['id']}",
            "title": h.get("type"),
            "street": addr.get("address"),
            "bairro": h.get("neighbourhood") or h.get("regionName"),
            "cidade": addr.get("city"),
            "rent": h.get("rentPrice"),
            "cond": h.get("condoIptu") or 0,  # QuintoAndar soma condomínio + IPTU
            "iptu": "incluso no condomínio",
            "area": h.get("area"),
            "quartos": h.get("bedrooms"),
            "banheiros": h.get("bathrooms"),
            "vagas": h.get("parkingSpots"),
            "amenities": am,
            "photos": [p["url"] for p in h.get("photos") or [] if p.get("url")][:30],
        })
    return out
