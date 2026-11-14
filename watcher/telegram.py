"""Envio de avisos para um canal do Telegram pela Bot API."""
from __future__ import annotations

import html

import requests


def brl(n: int | None) -> str:
    return "R$ " + f"{n:,}".replace(",", ".") if n else "—"


def format_message(l: dict, kind: str, alert_name: str, page_url: str | None, prev_total: int | None = None) -> str:
    total = (l.get("rent") or 0) + (l.get("cond") or 0)
    e = html.escape
    if kind == "novo":
        head = f"<b>Novo imóvel · {brl(total)}</b>"
    else:
        diff = (prev_total or total) - total
        head = f"<b>Baixou {brl(diff)} · agora {brl(total)}</b> (era {brl(prev_total)})"
    spec = " · ".join(x for x in [
        f"{l['area']} m²" if l.get("area") else None,
        f"{l['quartos']} quartos" if l.get("quartos") else None,
        f"{l['banheiros']} banheiros" if l.get("banheiros") else None,
        f"{l['vagas']} vaga(s)" if l.get("vagas") else None,
    ] if x)
    where = l.get("addr") or ", ".join(x for x in [l.get("street"), l.get("bairro"), l.get("cidade")] if x)
    lines = [
        head,
        f"aluguel {brl(l.get('rent'))} + cond. {brl(l.get('cond')) if l.get('cond') else '?'}",
        e(where or ""),
        e(spec),
    ]
    if l.get("pet") == "SIM":
        lines.append("Aceita pet (declarado no anúncio)")
    if l.get("nota"):
        lines.append(e(l["nota"]))
    links = [f'<a href="{e(l["url"])}">Ver anúncio</a>']
    if page_url:
        sep = "&" if "?" in page_url else "?"
        links.append(f'<a href="{e(page_url + sep + "anuncio=" + str(l["id"]))}">Abrir na lista</a>')
    lines += ["", " · ".join(links), f"<i>Alerta: {e(alert_name)}</i>"]
    return "\n".join(x for x in lines if x is not None)


class Telegram:
    def __init__(self, token: str | None, chat_id: str | None):
        self.token, self.chat_id = token, chat_id

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str, preview_url: str | None = None) -> bool:
        if not self.enabled:
            return False
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        if preview_url:
            payload["link_preview_options"] = {"url": preview_url, "prefer_large_media": True}
        r = requests.post(f"https://api.telegram.org/bot{self.token}/sendMessage", json=payload, timeout=30)
        return r.ok
