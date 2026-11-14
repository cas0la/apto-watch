"""OLX: os anúncios vêm no HTML do servidor, dentro dos blocos `self.__next_f.push([1,"..."])`."""
from __future__ import annotations

import json
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

PUSH = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', re.S)


def _int(s) -> int | None:
    d = re.sub(r"\D", "", str(s or ""))
    return int(d) if d else None


def page_url(url: str, page: int) -> str:
    parts = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "o"]
    if page > 1:
        q.append(("o", str(page)))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), ""))


def _js_string(s: str) -> str:
    try:
        return json.loads(f'"{s}"')
    except json.JSONDecodeError:
        return ""


def _ads(html: str) -> list[dict]:
    flight = "".join(_js_string(m) for m in PUSH.findall(html))
    m = re.search(r'\{"ads":\s*\[', flight)
    if not m:
        return []
    arr, _ = json.JSONDecoder().raw_decode(flight, m.end() - 1)
    return arr


def parse_list(html: str, source: str = "olx") -> list[dict]:
    out = []
    for ad in _ads(html):
        props = {p.get("name"): p.get("value") for p in ad.get("properties") or []}
        loc = ad.get("locationDetails") or {}
        feats = str(props.get("re_features") or "")
        rooms = props.get("rooms")
        out.append({
            "id": f"olx-{ad.get('listId')}",
            "source": source,
            "url": str(ad.get("url") or "").split("?")[0],
            "title": (ad.get("subject") or "")[:200] or None,
            "rent": _int(ad.get("priceValue") or ad.get("price")),
            "cond": _int(props.get("condominio")) or 0,
            "iptu": props.get("iptu") if _int(props.get("iptu")) else None,
            "area": _int(props.get("size")),
            "quartos": _int(rooms),
            "banheiros": _int(props.get("bathrooms")),
            "vagas": _int(props.get("garage_spaces")),
            "bairro": loc.get("neighbourhood") or None,
            "cidade": loc.get("municipality") or None,
            "addr": ad.get("location") or None,
            "amenities": [x.strip() for x in feats.split(",") if x.strip()],
            "photos": [im.get("original") for im in ad.get("images") or [] if im.get("original")][:30],
        })
    return out
