"""Ibagy Imóveis (ibagy.com.br).

A busca é guardada na sessão: GET /busca?<filtros>&pagina=N grava os filtros e redireciona
para /busca/, que devolve os cards `.imovel-box-single` (12 por página).
"""
from __future__ import annotations

import math
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

BASE = "https://ibagy.com.br"
PAGE_SIZE = 12


def _money(s) -> int | None:
    m = re.search(r"R\$\s*([\d.]+)(?:,\d{2})?", s or "")
    return int(m.group(1).replace(".", "")) if m else None


def _int(s) -> int | None:
    d = re.sub(r"\D", "", s or "")
    return int(d) if d else None


def page_url(url: str, page: int) -> str:
    sep = "&" if urlsplit(url).query else "?"
    return f"{url}{sep}pagina={page}"


def fetch_page(client, url: str, page: int) -> str:
    """Dois passos: grava os filtros na sessão e lê a página de resultados."""
    client.get(page_url(url, page))
    return client.get(f"{BASE}/busca/")


def total_pages(html: str) -> int | None:
    m = re.search(r"(\d[\d.]*)\s+im[óo]veis", BeautifulSoup(html, "lxml").get_text(" "))
    return math.ceil(int(m.group(1).replace(".", "")) / PAGE_SIZE) if m else None


def parse_list(html: str, source: str = "ibagy", assume: dict | None = None) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for box in soup.select(".imovel-box-single[data-codigo]"):
        cod = box["data-codigo"]
        a = box.find("a", href=re.compile(r"/imovel/"))
        title = box.select_one("h2")
        h3 = box.select_one("h3")
        addr_txt = h3.get_text(" ", strip=True) if h3 else ""
        # "Rua Azalea, 100, Barra Do Aririú - Palhoça /Sc NOME DO EMPREENDIMENTO"
        m = re.match(r"(.+?)\s+-\s+(.+?)\s*/\s*Sc\b", addr_txt, re.I)
        left, cidade = (m.group(1), m.group(2).strip()) if m else (addr_txt, None)
        parts = [p.strip() for p in left.split(",")]
        bairro = parts[-1] if len(parts) > 1 else None

        def cls(c):
            el = box.select_one(f".{c}")
            return el.get_text(" ", strip=True) if el else ""

        counts = {}
        for small in box.find_all("small"):
            prev = small.find_previous_sibling("span")
            label = small.get_text(strip=True).lower()
            if prev and prev.get_text(strip=True).isdigit():
                counts[label] = int(prev.get_text(strip=True))
        area = re.search(r"(\d+)\s*m²", title.get_text(" ") if title else "")
        photos = [re.sub(r"\?.*$", "", u) for u in re.findall(r"url\((https://[^)]+)\)", str(box.select_one(".swiper-container") or ""))]
        photos += [d for d in (s.get("data-background") for s in box.select("[data-background]")) if d]
        item = {
            "id": f"ibagy-{cod}",
            "source": source,
            "url": a["href"].split("?")[0] if a else f"{BASE}/imovel/{cod}/",
            "title": title.get_text(" ", strip=True) if title else None,
            "addr": f"{left} - {cidade} - SC" if cidade else addr_txt or None,
            "street": ", ".join(parts[:-1]) if len(parts) > 1 else None,
            "bairro": bairro,
            "cidade": cidade,
            "rent": _money(cls("item-price-rent")),
            "cond": _money(cls("item-price-condominio")) or 0,
            "iptu": (f"R$ {_money(cls('item-price-iptu'))}" if _money(cls("item-price-iptu")) else None),
            "area": int(area.group(1)) if area else None,
            "quartos": counts.get("quartos") or counts.get("quarto"),
            "vagas": counts.get("vagas") or counts.get("vaga"),
            "banheiros": None,
            "photos": list(dict.fromkeys(p.split("?")[0] for p in photos))[:30],
        }
        for k, v in (assume or {}).items():  # ex.: banheiros garantidos pelo filtro da busca
            if item.get(k) is None:
                item[k] = v
        out.append(item)
    return out
