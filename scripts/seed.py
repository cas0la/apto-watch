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
from watcher.store import Store, supabase_env  # noqa: E402


def main() -> int:
    load_dotenv(ROOT / ".env")
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
    problem = supabase_env(url, key)
    if problem:
        print(problem)
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
    import requests
    try:
        sys.exit(main())
    except requests.HTTPError as e:
        r = e.response
        hint = (" A tabela não existe: rode supabase/schema.sql no SQL Editor." if r is not None and r.status_code == 404
                else " Confira se SUPABASE_SERVICE_KEY é a service_role key, não a anon." if r is not None and r.status_code in (401, 403)
                else "")
        print(f"O Supabase recusou: HTTP {r.status_code if r is not None else '?'} {(r.text if r is not None else '')[:200]}{hint}")
        sys.exit(1)
    except requests.ConnectionError:
        print("Não deu para conectar ao Supabase. Confira a SUPABASE_URL no .env e a internet.")
        sys.exit(1)
