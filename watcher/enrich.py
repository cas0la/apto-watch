"""Locais de referência próximos (OpenStreetMap) e notas automáticas."""
from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path

POIS_FILE = Path(__file__).resolve().parent.parent / "data" / "pois.json"
CAT = {"mall": "Shopping", "supermarket": "Mercado", "university": "Faculdade",
       "hospital": "Hospital/UPA", "bus_station": "Terminal", "park": "Praça/parque"}
ORDER = ["Shopping", "Mercado", "Faculdade", "Hospital/UPA", "Terminal", "Praça/parque"]
LIMIT = {"Praça/parque": 600}
BAD = re.compile(r"Fazenda Experimental|Núcleo|Núclo|Secretaria|Centro Comercial|Comercial São|Galeria|"
                 r"TT Ponto|Camelódromo|Camelão|Mundo Car|Ceisa", re.I)
RENAME = {"Unisul Virtual": "Unisul (campus Pedra Branca)"}


@lru_cache(maxsize=1)
def _pois() -> list[tuple[str, str, float, float]]:
    if not POIS_FILE.exists():
        return []
    out = []
    for e in json.loads(POIS_FILE.read_text())["elements"]:
        t = e["tags"]
        k = t.get("shop") or t.get("amenity") or t.get("leisure")
        if k not in CAT or BAD.search(t.get("name", "")):
            continue
        la, lo = (e["lat"], e["lon"]) if "lat" in e else (e["center"]["lat"], e["center"]["lon"])
        out.append((CAT[k], RENAME.get(t["name"].strip(), t["name"].strip()), la, lo))
    return out


def _dist(a, b, c, d) -> float:
    r = 6371000
    p1, p2, dl = math.radians(a), math.radians(c), math.radians(d - b)
    return 2 * r * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def refs(lat: float | None, lon: float | None) -> list:
    if lat is None or lon is None:
        return []
    best: dict = {}
    for c, n, a, b in _pois():
        m = _dist(lat, lon, a, b)
        if m > LIMIT.get(c, 3000):
            continue
        if c not in best or m < best[c][1]:
            best[c] = (n, m)
    return [[c, best[c][0], int(round(best[c][1] / 50) * 50)] for c in ORDER if c in best]


NOTES = [
    (re.compile(r"vaga[^.]{0,40}\bmoto\b", re.I), "A vaga pode ser só para moto: confirme"),
    (re.compile(r"sem elevador|n[ãa]o possui elevador", re.I), "Prédio sem elevador"),
    (re.compile(r"casa t[ée]rre[ao]", re.I), "Anúncio descreve uma casa térrea"),
    (re.compile(r"em obras", re.I), "Anúncio cita obras no condomínio"),
]


def auto_note(text: str) -> str | None:
    found = [msg for rx, msg in NOTES if rx.search(text or "")]
    return "; ".join(found) or None
