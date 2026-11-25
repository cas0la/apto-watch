"""Reaplica os critérios do config.yaml aos anúncios ativos que já estão no banco.

Quem não passa mais (bairro fora da lista, mobiliado, temporada, preço) é apagado; o watcher não volta a
gravá-lo enquanto o critério valer. Favoritos ficam e são listados para a decisão de vocês.
Também recalcula a região (ex.: "Palhoça" no lugar de "Pedra Branca (Palhoça)").

Uso:
  .venv/bin/python scripts/reaplicar_criterios.py            # só mostra
  .venv/bin/python scripts/reaplicar_criterios.py --apply    # grava
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from watcher import criteria  # noqa: E402
from watcher.store import Store  # noqa: E402


def main(apply: bool) -> int:
    load_dotenv()
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), encoding="utf-8"))
    st = Store(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    rows = st._get("listings", {"select": "*", "active": "is.true"})
    favs = {m["listing_id"] for m in st._get("marks", {"select": "listing_id,status", "status": "eq.fav"})}
    why, out, kept = Counter(), [], []
    for l in rows:
        reg = criteria.regiao(l.get("cidade"))
        if apply and reg and reg != l.get("regiao"):
            st.update_listing(l["id"], {"regiao": reg})
        ok, reason = criteria.base_ok({**l, "regiao": reg}, cfg["criteria"])
        if ok:
            continue
        why[reason.split(" (")[0] if not reason.startswith("bairro") else "bairro fora da lista"] += 1
        (kept if l["id"] in favs else out).append((l, reason))
    print(f"{len(rows)} ativos; saem {len(out)}; favoritos mantidos {len(kept)}")
    for k, n in why.most_common():
        print(f"  {n:4}  {k}")
    for l, reason in kept:
        print(f"  favorito fora do critério: {l['id']} {l.get('street') or l.get('bairro')} ({reason})")
    if apply:
        for l, _ in out:
            st.s.delete(f"{st.base}/listings", params={"id": f"eq.{l['id']}"}, timeout=30).raise_for_status()
        print(f"{len(out)} apagados")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
