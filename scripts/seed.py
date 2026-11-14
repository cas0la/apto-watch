"""Importa os anúncios e as marcas da página antiga (claude.ai) para o Supabase.

Uso (uma vez, depois de rodar supabase/schema.sql):
    python scripts/seed.py
Pode rodar de novo sem duplicar: faz upsert pelos códigos.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from watcher.store import Store  # noqa: E402


def main() -> int:
    load_dotenv(ROOT / ".env")
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    if not (url and key):
        print("Defina SUPABASE_URL e SUPABASE_SERVICE_KEY no .env.")
        return 1
    st = Store(url, key)
    listings = json.loads((ROOT / "seed/listings.json").read_text())
    marks = json.loads((ROOT / "seed/marks.json").read_text())
    st.upsert_listings(listings)
    existing = {r["listing_id"] for r in st._get("price_history", {"select": "listing_id"})}
    hist = [{"listing_id": l["id"], "total": (l["rent"] or 0) + (l["cond"] or 0), "seen_at": l["first_seen"]}
            for l in listings if l["id"] not in existing]
    if hist:
        st._post("price_history", hist)
    st._post("marks", marks, upsert=True)
    print(f"{len(listings)} anúncios e {len(marks)} marcas importados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
