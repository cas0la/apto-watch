"""Acesso ao Supabase pela API REST (PostgREST), com a service_role key do .env."""
from __future__ import annotations

import re
from datetime import datetime, timezone

import requests

LISTING_FIELDS = {
    "id", "source", "url", "title", "addr", "street", "bairro", "cidade", "regiao", "rent", "cond", "iptu",
    "area", "quartos", "banheiros", "vagas", "amenities", "descricao", "pet", "pet_neg", "photos", "lat", "lon",
    "refs", "nota", "first_seen", "last_seen", "details_at", "prev_total", "price_drop_at", "active", "alt_urls", "inactive_at", "anunciante",
}


def supabase_env(url: str | None, key: str | None) -> str | None:
    """Devolve o problema do .env em uma frase, ou None se parece preenchido."""
    if not (url and key):
        return "Defina SUPABASE_URL e SUPABASE_SERVICE_KEY no .env."
    if "SEU-PROJETO" in url.upper() or key.startswith("cole-"):
        return ("O .env ainda tem os valores de exemplo. Troque SUPABASE_URL pela Project URL e "
                "SUPABASE_SERVICE_KEY pela service_role key (Supabase > Project Settings > API Keys).")
    if not url.startswith("https://") or ".supabase.co" not in url:
        return f"SUPABASE_URL não parece a Project URL do Supabase (esperado https://xxxx.supabase.co): {url}"
    return None


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
        return self._get("listings", {"select": "id,source,url,lat,lon", "details_at": "is.null",
                                      "source": "in.(vivareal,zap,isci)", "active": "is.true", "limit": str(limit)})

    def upsert_listings(self, rows: list[dict]):
        rows = [{k: v for k, v in r.items() if k in LISTING_FIELDS} for r in rows]
        # O PostgREST exige as mesmas chaves em todas as linhas de um envio (PGRST102):
        # anúncios com e sem detalhe vão em lotes separados.
        groups: dict[tuple, list[dict]] = {}
        for r in rows:
            groups.setdefault(tuple(sorted(r)), []).append(r)
        for group in groups.values():
            for i in range(0, len(group), 200):
                self._post("listings", group[i:i + 200], upsert=True)

    def find_duplicate(self, l: dict, street_key: str | None = None) -> dict | None:
        """Mesmo imóvel já gravado (outro site ou outra imobiliária): ver criteria.mesmo_imovel."""
        from .criteria import mesmo_imovel  # import tardio para evitar ciclo
        if not l.get("area") or not l.get("cidade"):
            return None
        total = (l.get("rent") or 0) + (l.get("cond") or 0)
        rows = self._get("listings", {"select": "id,source,street,addr,bairro,cidade,area,quartos,banheiros,total,alt_urls",
                                      "active": "is.true",
                                      "and": f"(total.gte.{total - 150},total.lte.{total + 150})"})
        return next((r for r in rows if r["id"] != l.get("id") and mesmo_imovel(l, r)), None)

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

    # pedidos de "Buscar agora"
    def claim_sync_requests(self) -> list[int]:
        """Marca os pedidos pendentes como 'rodando' e devolve os ids."""
        rows = self._get("sync_requests", {"select": "id", "status": "eq.pendente"})
        ids = [r["id"] for r in rows]
        if ids:
            self._patch("sync_requests", {"id": f"in.({','.join(map(str, ids))})"},
                        {"status": "rodando", "started_at": now()})
        return ids

    def finish_sync_requests(self, ids: list[int], status: str, message: str):
        if ids:
            self._patch("sync_requests", {"id": f"in.({','.join(map(str, ids))})"},
                        {"status": status, "finished_at": now(), "message": message[:500]})

    def last_run_started(self) -> str | None:
        rows = self._get("runs", {"select": "started_at", "order": "started_at.desc", "limit": "1"})
        return rows[0]["started_at"] if rows else None

    # execuções
    def start_run(self, source: str) -> int:
        return self._post("runs", [{"source": source, "status": "rodando"}], ret=True)[0]["id"]

    def finish_run(self, run_id: int, **data):
        data["finished_at"] = now()
        self._patch("runs", {"id": f"eq.{run_id}"}, data)
