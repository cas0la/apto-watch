"""Cliente HTTP educado: identifica o robô, respeita o robots.txt, espera entre requisições
e para quando o site bloqueia.

Não tenta contornar bloqueios: sem trocar User-Agent, sem resolver desafios, sem proxies.
Se o site devolver 401/403/429/503, uma página de desafio, ou o robots.txt proibir o caminho,
a fonte é encerrada nesta execução. Sites assim ficam na coleta assistida.
"""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlsplit

import requests

CHALLENGE_MARKERS = ("cf-chl", "challenge-platform", "Just a moment", "Um momento…", "Attention Required")


class Blocked(Exception):
    """O site recusou, desafiou ou proibiu a requisição. A execução dessa fonte deve parar."""


class NotFound(Exception):
    """O anúncio saiu do ar (404/410)."""


class PoliteClient:
    def __init__(self, user_agent: str, delay_seconds: float):
        self.ua = user_agent
        self.delay = max(float(delay_seconds), 3.0)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Language": "pt-BR,pt;q=0.9"})
        self._last = 0.0
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.requests = 0

    def _wait(self):
        wait = self._last + self.delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def allowed(self, url: str) -> bool:
        p = urlsplit(url)
        host = f"{p.scheme}://{p.netloc}"
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            self._wait()
            try:
                r = self.session.get(host + "/robots.txt", timeout=20)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
                if r.status_code in (401, 403):
                    rp.disallow_all = True
            except requests.RequestException:
                rp.parse([])
            self._robots[host] = rp
        return self._robots[host].can_fetch(self.ua, url)

    def get(self, url: str) -> str:
        if not self.allowed(url):
            raise Blocked("robots.txt não permite este caminho")
        self._wait()
        self.requests += 1
        try:
            r = self.session.get(url, timeout=30)
        except requests.RequestException as e:  # rede fora, timeout
            raise Blocked(f"falha de rede: {e.__class__.__name__}") from e
        if r.status_code in (404, 410):
            raise NotFound(url)
        if r.status_code >= 400:
            raise Blocked(f"HTTP {r.status_code}")
        head = r.text[:4000]
        if any(m in head for m in CHALLENGE_MARKERS):
            raise Blocked("página de desafio anti-robô")
        return r.text
