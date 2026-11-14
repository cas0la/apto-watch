"""Uso:
    python -m watcher              # execução normal (grava no Supabase e avisa no Telegram)
    python -m watcher --dry-run    # só lê as buscas e mostra o que entraria; não grava nada
    python -m watcher --test-telegram   # manda uma mensagem de teste para o canal
    python -m watcher --ingest coleta.json   # importa a coleta assistida dos portais (ver .claude/skills)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .run import ingest_file, process, run
from .store import Store
from .telegram import Telegram

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    p = argparse.ArgumentParser(prog="apto-watch")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--test-telegram", action="store_true")
    p.add_argument("--ingest", metavar="ARQUIVO", help="JSON da coleta assistida")
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
        if not (url and key):
            print("Defina SUPABASE_URL e SUPABASE_SERVICE_KEY no .env (ou use --dry-run).")
            return 1
        store = Store(url, key)

    if args.ingest:
        if store is None:
            print("--ingest grava no Supabase; não combina com --dry-run.")
            return 1
        seen, report = ingest_file(args.ingest)
        summary = process(cfg, store, tg, seen, report, None, os.getenv("PAGE_URL"))
    else:
        summary = run(cfg, store, tg, page_url=os.getenv("PAGE_URL"), dry=args.dry_run)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("report", "sample")}, ensure_ascii=False))
    for line in summary.get("sample", []):
        print("  entraria:", line)
    for r in summary["report"]:
        print(f"  {r['source']:9} {r['status']:10} {r['pages']} pág, {r['found']} cards  {r['message']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
