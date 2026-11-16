"""Recebe o JSON da coleta assistida por POST e grava em <pasta>/<nome>.json. Só escuta em 127.0.0.1:8767.

Uso: python3 scripts/receive_collection.py coleta   (Ctrl+C para parar)
"""
import json, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
OUT = sys.argv[1]
class H(BaseHTTPRequestHandler):
    def _cors(self):
        o = self.headers.get("Origin") or ""
        if re.fullmatch(r"https://www\.(vivareal|olx)\.com\.br", o):
            self.send_header("Access-Control-Allow-Origin", o)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        name = re.sub(r"[^a-z0-9-]", "", self.path.strip("/"))[:40] or "coleta"
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with open(f"{OUT}/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(str(len(data)).encode())
    def log_message(self, *a): pass
HTTPServer(("127.0.0.1", 8767), H).serve_forever()
