"""Junta anúncios duplicados que já estão no banco (o mesmo apartamento em sites ou imobiliárias diferentes).

Usa a mesma regra do watcher (criteria.mesmo_imovel). Em cada grupo fica um anúncio principal; os outros
viram links em `alt_urls` e são apagados. Marcações (favorito, descarte, alugado) e "visto" dos duplicados
passam para o principal quando ele não tem a sua.

Uso:
  .venv/bin/python scripts/dedupe.py            # só mostra os grupos
  .venv/bin/python scripts/dedupe.py --apply    # grava
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv  # noqa: E402

from watcher.criteria import mesmo_imovel  # noqa: E402
from watcher.store import Store  # noqa: E402

# Imobiliária lida direto (atualizada a cada 3 h) antes de portal; portal com detalhe antes do OLX.
RANK = {"ibagy": 0, "isci": 0, "quintoandar": 0, "vivareal": 1, "zap": 2, "olx": 3}
FILL = ("descricao", "amenities", "photos", "lat", "lon", "refs", "addr", "iptu", "anunciante", "street", "details_at")


def groups(rows: list[dict]) -> list[list[dict]]:
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if mesmo_imovel(rows[i], rows[j]):
                parent[find(i)] = find(j)
    out: dict[int, list[dict]] = {}
    for i, r in enumerate(rows):
        out.setdefault(find(i), []).append(r)
    return [g for g in out.values() if len(g) > 1]


def main(apply: bool) -> int:
    load_dotenv()
    st = Store(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    rows = st._get("listings", {"select": "*", "active": "is.true"})
    marks = {m["listing_id"]: m for m in st._get("marks", {"select": "*"})}
    rentals = {m["listing_id"]: m for m in st._get("rentals", {"select": "*"})}
    try:
        views = st._get("views", {"select": "*"})
    except Exception:
        views = []
    gs = groups(rows)

    def key(r):
        m = marks.get(r["id"], {}).get("status")
        return (0 if m == "fav" else 1 if r["id"] in rentals or m else 2, RANK.get(r["source"], 4),
                -(len(r.get("photos") or []) + (50 if r.get("descricao") else 0)), r["first_seen"])

    removed = 0
    for g in gs:
        g.sort(key=key)
        # Só junta quem bate direto com o principal (a regra não é transitiva: A~B e B~C não garante A~C).
        main_, dups = g[0], [d for d in g[1:] if mesmo_imovel(g[0], d)]
        if not dups:
            continue
        print(f"{main_['id']} ({main_['source']}, R$ {main_['total']}, {main_.get('street') or main_.get('bairro')})"
              f"  <=  " + ", ".join(f"{d['id']} ({d['source']}, R$ {d['total']})" for d in dups))
        if not apply:
            continue
        alt = list(main_.get("alt_urls") or [])
        upd: dict = {}
        for d in dups:
            alt.append({"source": d["source"], "url": d["url"], "anunciante": d.get("anunciante")})
            alt += d.get("alt_urls") or []
            for k in FILL:
                if not main_.get(k) and d.get(k) and k not in upd:
                    upd[k] = d[k]
            if main_.get("pet") == "?" and d.get("pet") in ("SIM", "NAO") and "pet" not in upd:
                upd["pet"], upd["pet_neg"] = d["pet"], d.get("pet_neg")
            if d["id"] in marks and main_["id"] not in marks:
                m = {**marks[d["id"]], "listing_id": main_["id"]}
                st._post("marks", [m], upsert=True)
                marks[main_["id"]] = m
            if d["id"] in rentals and main_["id"] not in rentals:
                r = {**rentals[d["id"]], "listing_id": main_["id"]}
                st._post("rentals", [r], upsert=True)
                rentals[main_["id"]] = r
            for v in [v for v in views if v["listing_id"] == d["id"]]:
                st._post("views", [{**v, "listing_id": main_["id"]}], upsert=True)
        seen_urls, uniq = {main_["url"]}, []
        for a in alt:
            if a.get("url") and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                uniq.append(a)
        st.update_listing(main_["id"], {**upd, "alt_urls": uniq})
        for d in dups:
            st.s.delete(f"{st.base}/listings", params={"id": f"eq.{d['id']}"}, timeout=30).raise_for_status()
            removed += 1
    print(f"{len(gs)} grupos" + (f"; {removed} duplicados apagados" if apply else " (simulação)"))
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
