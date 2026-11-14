"""Uso:
    python -m watcher              # execução normal (grava no Supabase e avisa no Telegram)
    python -m watcher --dry-run    # só lê as buscas e mostra o que entraria; não grava nada
    python -m watcher --test-telegram   # manda uma mensagem de teste para o canal
    python -m watcher --ingest coleta.json   # importa a coleta assistida dos portais (ver .claude/skills)
    python -m watcher --if-requested   # só roda se alguém tocou em "Buscar agora" na página (timer de 5 min)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .run import ingest_file, process, run
from .store import Store, supabase_env
from .telegram import Telegram

ROOT = Path(__file__).resolve().parent.parent
MIN_GAP_MIN = 20  # um pedido feito logo depois de uma leitura não lê as fontes de novo


def minutes_since(iso: str | None) -> float | None:
    if not iso:
        return None
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - t).total_seconds() / 60


def sync_message(summary: dict) -> str:
    n, d = summary.get("new", 0), summary.get("drops", 0)
    parts = [f"{n} {'anúncio novo' if n == 1 else 'anúncios novos'}"]
    if d:
        parts.append(f"{d} {'redução' if d == 1 else 'reduções'} de preço")
    bad = sorted({r["source"] for r in summary.get("report", []) if r["status"] != "ok"})
    if bad:
        parts.append("sem resposta de " + ", ".join(bad))
    return " · ".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(prog="apto-watch")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--test-telegram", action="store_true")
    p.add_argument("--ingest", metavar="ARQUIVO", help="JSON da coleta assistida")
    p.add_argument("--if-requested", action="store_true", help="só roda se houver pedido de 'Buscar agora'")
    p.add_argument("--config", default=str(ROOT / "config.yaml"))
    args = p.parse_args()

    load_dotenv(ROOT / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = yaml.safe_load(Path(args.config).read_text())
    tg = Telegram(os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"))

    if args.test_telegram:
        if not tg.enabled:
            print("Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env.")
            return 1
        ok = tg.send("apto-watch conectado. Os alertas de imóveis chegam neste canal.")
        print("Mensagem enviada." if ok else "O Telegram recusou: confira o token, o chat_id e se o bot é admin do canal.")
        return 0 if ok else 1

    store = None
    if not args.dry_run:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY")
        problem = supabase_env(url, key)
        if problem:
            print(problem + " Para testar sem gravar, use --dry-run.")
            return 1
        store = Store(url, key)

    if args.ingest:
        if store is None:
            print("--ingest grava no Supabase; não combina com --dry-run.")
            return 1
        seen, report = ingest_file(args.ingest)
        summary = process(cfg, store, tg, seen, report, None, os.getenv("PAGE_URL"))
    else:
        # Toda leitura completa atende os pedidos de "Buscar agora" que estiverem na fila.
        requests_ids = store.claim_sync_requests() if store else []
        if args.if_requested:
            if not requests_ids:
                return 0
            gap = minutes_since(store.last_run_started())
            if gap is not None and gap < MIN_GAP_MIN:
                store.finish_sync_requests(requests_ids, "ok", f"As fontes foram lidas há {max(1, round(gap))} min; "
                                                               "a lista já está atualizada.")
                print("Pedido atendido sem nova leitura: leitura recente.")
                return 0
        try:
            summary = run(cfg, store, tg, page_url=os.getenv("PAGE_URL"), dry=args.dry_run)
        except Exception as e:
            if store:
                store.finish_sync_requests(requests_ids, "erro", f"A busca falhou: {e}")
            raise
        if store:
            store.finish_sync_requests(requests_ids, "ok", sync_message(summary))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("report", "sample")}, ensure_ascii=False))
    for line in summary.get("sample", []):
        print("  entraria:", line)
    for r in summary["report"]:
        print(f"  {r['source']:9} {r['status']:10} {r['pages']} pág, {r['found']} cards  {r['message']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
