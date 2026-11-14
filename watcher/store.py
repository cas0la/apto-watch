"""Acesso ao Supabase pela API REST (PostgREST), com a service_role key do .env."""
from __future__ import annotations

import re
from datetime import datetime, timezone

import requests

LISTING_FIELDS = {
    "id", "source", "url", "title", "addr", "street", "bairro", "cidade", "regiao", "rent", "cond", "iptu",
    "area", "quartos", "banheiros", "vagas", "amenities", "descricao", "pet", "pet_neg", "photos", "lat", "lon",
    "refs", "nota", "first_seen", "last_seen", "details_at", "prev_total", "price_drop_at", "active", "alt_urls", "inactive_at",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, url: str, service_key: str):
        self.base = url.rstrip("/") + "/rest/v1"
        self.s = requests.Session()
        self.s.headers.update({"apikey": service_key, "Authorization": f"Bearer {service_key}",
                               "Content-Type": "application/json"})

    def _get(self, table: str, params: dict) -> list[dict]:
        r = self.s.get(f"{self.base}/{table}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def _post(self, table: str, rows, upsert: bool = False, ignore_dupes: bool = False, ret: bool = False):
        prefer = []
        if upsert:
            prefer.append("resolution=merge-duplicates")
        if ignore_dupes:
            prefer.append("resolution=ignore-duplicates")
        prefer.append("return=representation" if ret else "return=minimal")
        r = self.s.post(f"{self.base}/{table}", json=rows, headers={"Prefer": ",".join(prefer)}, timeout=60)
        r.raise_for_status()
        return r.json() if ret else None

    def _patch(self, table: str, filters: dict, data: dict):
        r = self.s.patch(f"{self.base}/{table}", params=filters, json=data, timeout=30)
        r.raise_for_status()

    # anúncios
    def listings_by_id(self, ids: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            rows = self._get("listings", {"select": "id,total,rent,cond,details_at,photos,price_drop_at,descricao,"
                                                    "amenities,lat,lon,refs,addr,alt_urls",
                                          "id": f"in.({','.join(chunk)})"})
            out.update({r["id"]: r for r in rows})
        return out

    def listings_missing_details(self, limit: int) -> list[dict]:
        return self._get("listings", {"select": "id,source,lat,lon", "details_at": "is.null",
                                      "source": "in.(vivareal,zap)", "active": "is.true", "limit": str(limit)})

    def upsert_listings(self, rows: list[dict]):
        rows = [{k: v for k, v in r.items() if k in LISTING_FIELDS} for r in rows]
        for i in range(0, len(rows), 200):
            self._post("listings", rows[i:i + 200], upsert=True)

    def find_duplicate(self, l: dict, street_key: str) -> dict | None:
        """Mesmo imóvel anunciado em outro site: mesma rua e número, total e área parecidos."""
        if not street_key or not re.search(r"\d", street_key):
            return None
        total = (l.get("rent") or 0) + (l.get("cond") or 0)
        rows = self._get("listings", {"select": "id,source,street,addr,area,alt_urls", "active": "is.true",
                                      "source": f"neq.{l['source']}", "and": f"(total.gte.{total - 80},total.lte.{total + 80})"})
        from .run import _street_key  # import tardio para evitar ciclo
        for r in rows:
            if _street_key(r) == street_key and (not l.get("area") or not r.get("area") or abs(r["area"] - l["area"]) <= 3):
                return r
        return None

    def add_alt_url(self, listing_id: str, current: list, item: dict):
        if any(x.get("url") == item["url"] for x in current):
            return
        self._patch("listings", {"id": f"eq.{listing_id}"}, {"alt_urls": current + [item]})

    def update_listing(self, listing_id: str, data: dict):
        self._patch("listings", {"id": f"eq.{listing_id}"}, {k: v for k, v in data.items() if k in LISTING_FIELDS})

    def add_price(self, listing_id: str, total: int):
        self._post("price_history", [{"listing_id": listing_id, "total": total}])

    def deactivate_stale(self, sources: list[str], before_iso: str):
        if sources:
            self._patch("listings", {"source": f"in.({','.join(sources)})", "last_seen": f"lt.{before_iso}",
                                     "active": "is.true"}, {"active": False, "inactive_at": now()})

    # marcas, alertas, avisos
    def marks(self) -> dict[str, dict]:
        return {r["listing_id"]: r for r in self._get("marks", {"select": "listing_id,status,at"})}

    def alerts(self) -> list[dict]:
        return self._get("alerts", {"select": "*", "enabled": "is.true"})

    def sent(self, listing_id: str, alert_id: str, kind: str) -> bool:
        return bool(self._get("notifications", {"select": "listing_id", "listing_id": f"eq.{listing_id}",
                                                "alert_id": f"eq.{alert_id}", "kind": f"eq.{kind}"}))

    def mark_sent(self, listing_id: str, alert_id: str, kind: str):
        self._post("notifications", [{"listing_id": listing_id, "alert_id": alert_id, "kind": kind}],
                   ignore_dupes=True)

    # execuções
    def start_run(self, source: str) -> int:
        return self._post("runs", [{"source": source, "status": "rodando"}], ret=True)[0]["id"]

    def finish_run(self, run_id: int, **data):
        data["finished_at"] = now()
        self._patch("runs", {"id": f"eq.{run_id}"}, data)
