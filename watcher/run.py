"""Processamento comum do watcher automático e da coleta assistida.

- `collect()` percorre as buscas automáticas (sites que aceitam robô identificado).
- `ingest_file()` lê o JSON produzido pela coleta assistida (portais que recusam robô).
- `process()` grava novidades, detecta reduções de preço, junta duplicados e dispara alertas.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone

from . import criteria, enrich
from .http import Blocked, NotFound, PoliteClient
from .sources import ibagy, isci, olx, quintoandar, vivareal
from .store import Store, now
from .telegram import Telegram, format_message

log = logging.getLogger("apto-watch")
MODULES = {"vivareal": vivareal, "zap": vivareal, "olx": olx, "ibagy": ibagy, "quintoandar": quintoandar, "isci": isci}
DETAIL_SOURCES = {"vivareal", "zap", "isci"}  # fontes com página de detalhe lida pelo watcher
JUDGE_AFTER_DETAIL = {"vivareal", "zap"}       # o card não basta para julgar: lê o detalhe antes dos critérios


def _normalize(l: dict) -> dict:
    l["regiao"] = criteria.regiao(l.get("cidade"))
    if not l.get("addr"):
        l["addr"] = ", ".join(x for x in [l.get("street"), l.get("bairro"), l.get("cidade")] if x) or None
    text = " ".join([l.get("descricao") or "", " ".join(l.get("amenities") or []), l.get("title") or ""])
    pet, neg = criteria.pet_status(text)
    l["pet"], l["pet_neg"] = pet, neg
    l["nota"] = l.get("nota") or enrich.auto_note(text)
    if l.get("lat") is not None and not l.get("refs"):
        l["refs"] = enrich.refs(l.get("lat"), l.get("lon"))
    return l


def _total(l: dict) -> int:
    return (l.get("rent") or 0) + (l.get("cond") or 0)


def _street_key(l: dict) -> str:
    s = criteria.norm(l.get("street") or (l.get("addr") or "").split(" - ")[0])
    s = re.sub(r"^(rua|r\.|avenida|av\.?|travessa|servidao|rodovia)\s+", "", s)
    return re.sub(r"[^a-z0-9 ]", "", s).strip()


def collect(cfg: dict, client: PoliteClient) -> tuple[dict[str, dict], list[dict]]:
    """Percorre as buscas automáticas. Devolve (anúncios por id, relatório por busca)."""
    seen: dict[str, dict] = {}
    report = []
    blocked: set[str] = set()
    max_pages = cfg.get("max_pages_per_search", 4)
    for s in cfg["searches"]:
        src, url = s["source"], s["url"]
        if s.get("modo", "auto") != "auto":
            continue
        mod = MODULES[src]
        rep = {"source": src, "url": url, "pages": 0, "found": 0, "status": "ok", "message": "", "complete": False}
        if src in blocked:
            rep.update(status="bloqueado", message="fonte bloqueada antes nesta execução")
            report.append(rep)
            continue
        try:
            last = max_pages
            for page in range(1, max_pages + 1):
                html = mod.fetch_page(client, url, page) if hasattr(mod, "fetch_page") else client.get(mod.page_url(url, page))
                items = mod.parse_list(html, src, s["assume"]) if s.get("assume") else mod.parse_list(html, src)
                rep["pages"] += 1
                rep["found"] += len(items)
                for it in items:
                    seen.setdefault(it["id"], _normalize(it))
                if page == 1:
                    tp = mod.total_pages(html) if hasattr(mod, "total_pages") else (1 if mod is quintoandar else None)
                    if tp:
                        last = min(last, tp)
                        rep["complete"] = tp <= max_pages
                if not items or page >= last:
                    rep["complete"] = rep["complete"] or not items
                    break
        except Blocked as e:
            rep.update(status="bloqueado", message=str(e))
            blocked.add(src)
        except Exception as e:  # HTML mudou, erro de parse etc.
            log.exception("erro na busca %s", url)
            rep.update(status="erro", message=f"{e.__class__.__name__}: {e}"[:300])
        log.info("%s %s: %s páginas, %s cards, %s", src, url[:80], rep["pages"], rep["found"], rep["status"])
        report.append(rep)
    return seen, report


def ingest_file(path: str) -> tuple[dict[str, dict], list[dict]]:
    """Lê a coleta assistida: lista de anúncios no mesmo formato dos leitores (ver SKILL)."""
    rows = json.loads(open(path, encoding="utf-8").read())
    seen = {}
    for r in rows:
        r.setdefault("source", "vivareal")
        if r.get("details_at") is None and r.get("descricao"):
            r["details_at"] = now()
        seen[str(r["id"])] = _normalize(r)
    srcs = sorted({r["source"] for r in seen.values()})
    report = [{"source": s, "url": "coleta assistida", "pages": 0, "found": sum(1 for r in seen.values() if r["source"] == s),
               "status": "ok", "message": "coleta assistida", "complete": False} for s in srcs]
    return seen, report


def fetch_details(client: PoliteClient, l: dict) -> dict:
    """Completa um anúncio com a página de detalhe (VivaReal/ZAP só se o site aceitar; Isci)."""
    try:
        if l.get("source") == "isci":
            d = isci.parse_detail(client.get(l["url"]))
        else:
            d = vivareal.parse_detail(client.get(vivareal.detail_url(l["id"])))
    except NotFound:
        return {"active": False}
    d["details_at"] = now()
    if d.get("lat") is not None:
        d["refs"] = enrich.refs(d.get("lat"), d.get("lon"))
    if d.get("descricao") or d.get("amenities"):  # anúncio já gravado: o pet também vem do texto novo
        d["pet"], d["pet_neg"] = criteria.pet_status(" ".join([d.get("descricao") or "", " ".join(d.get("amenities") or [])]))
    return d


def process(cfg: dict, store: Store, tg: Telegram | None, seen: dict[str, dict], report: list[dict],
            client: PoliteClient | None = None, page_url: str | None = None) -> dict:
    crit = cfg["criteria"]
    started = datetime.now(timezone.utc)
    summary = {"cards": len(seen), "new": 0, "drops": 0, "dupes": 0, "alerts": 0, "details": 0, "report": report}
    existing = store.listings_by_id(list(seen))
    detail_budget = cfg.get("detail_limit", 25) if client else 0
    new_rows, drops = [], []

    for lid, l in seen.items():
        ex = existing.get(lid)
        if ex is None:
            if not criteria.base_ok(l, crit)[0] and l.get("source") not in JUDGE_AFTER_DETAIL:
                continue
            if l["source"] in DETAIL_SOURCES and not l.get("details_at") and detail_budget > 0:
                try:
                    l.update(fetch_details(client, l))
                    detail_budget -= 1
                    summary["details"] += 1
                except Blocked as e:
                    detail_budget = 0
                    log.warning("detalhes interrompidos: %s", e)
                _normalize(l)
            if not criteria.base_ok(l, crit)[0]:
                continue
            dup = store.find_duplicate(l, _street_key(l))
            if dup:
                store.add_alt_url(dup["id"], dup.get("alt_urls") or [], {"source": l["source"], "url": l["url"]})
                summary["dupes"] += 1
                continue
            l["first_seen"] = l["last_seen"] = now()
            l["active"] = True
            new_rows.append(l)
            continue
        upd = {"last_seen": now(), "active": True, "inactive_at": None}  # voltou a aparecer: não foi alugado
        total = _total(l)
        if l.get("rent") and total != ex["total"]:
            upd.update(rent=l["rent"], cond=l.get("cond") or 0)
            store.add_price(lid, total)
            if total < ex["total"]:
                upd.update(prev_total=ex["total"], price_drop_at=now())
                drops.append((lid, l, ex["total"]))
        for k in ("descricao", "amenities", "photos", "lat", "lon", "refs", "addr", "details_at"):
            if l.get(k) and not ex.get(k):  # completa o que faltava, sem apagar o que já existe
                upd[k] = l[k]
        store.update_listing(lid, upd)

    if new_rows:
        store.upsert_listings(new_rows)
        for l in new_rows:
            store.add_price(l["id"], _total(l))
    summary["new"], summary["drops"] = len(new_rows), len(drops)

    if client and detail_budget > 0:
        for row in store.listings_missing_details(detail_budget):
            try:
                d = fetch_details(client, row)
            except Blocked as e:
                log.warning("detalhes interrompidos: %s", e)
                break
            store.update_listing(row["id"], d)
            summary["details"] += 1

    if tg and tg.enabled:
        alerts = store.alerts()
        for l in new_rows:
            for a in alerts:
                if criteria.alert_match(l, a) and not store.sent(l["id"], a["id"], "novo"):
                    if tg.send(format_message(l, "novo", a["name"], page_url), l["url"]):
                        store.mark_sent(l["id"], a["id"], "novo")
                        summary["alerts"] += 1
        for lid, l, old in drops:
            kind = f"reducao:{_total(l)}"
            for a in alerts:
                if a.get("avisar_reducao") and criteria.alert_match(l, a) and not store.sent(lid, a["id"], kind):
                    if tg.send(format_message(l, "reducao", a["name"], page_url, old), l["url"]):
                        store.mark_sent(lid, a["id"], kind)
                        summary["alerts"] += 1

    by_src: dict[str, bool] = {}
    for r in report:
        by_src[r["source"]] = by_src.get(r["source"], True) and r["status"] == "ok" and r["complete"]
    store.deactivate_stale([s for s, ok in by_src.items() if ok], (started - timedelta(days=7)).isoformat())

    counted: set[str] = set()
    for r in report:
        first = r["source"] not in counted
        counted.add(r["source"])
        rid = store.start_run(r["source"])
        store.finish_run(rid, status=r["status"], pages=r["pages"], found=r["found"],
                         new_count=sum(1 for l in new_rows if l["source"] == r["source"]) if first else 0,
                         drops=sum(1 for _, l, _ in drops if l["source"] == r["source"]) if first else 0,
                         message=(r["message"] or r["url"])[:500])
    return summary


def run(cfg: dict, store: Store | None, tg: Telegram | None, page_url: str | None = None, dry: bool = False) -> dict:
    client = PoliteClient(cfg["user_agent"], cfg.get("delay_seconds", 10))
    seen, report = collect(cfg, client)
    if dry or store is None:
        ok = {i: l for i, l in seen.items() if criteria.base_ok(l, cfg["criteria"])[0]}
        return {"cards": len(seen), "new": len(ok), "drops": 0, "alerts": 0, "details": 0, "report": report,
                "sample": [f"{l['id']} {_total(l)} {l.get('bairro')}/{l.get('cidade')}" for l in list(ok.values())[:10]]}
    return process(cfg, store, tg, seen, report, client, page_url)
