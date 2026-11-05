"""Local visual-QA server: serves app/static + canned API fixtures (no deps). Usage: python3 mock_server.py <fixtures_dir> <assets_dir> <static_dir> <port>"""
import http.server, json, os, sys
FX, ASSETS, STATIC, PORT = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
class H(http.server.BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        self.send_response(200); self.send_header("Content-Type", ctype); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/": return self._send(open(f"{STATIC}/index.html", "rb").read(), "text/html")
        if p.startswith("/static/"):
            f = f"{STATIC}/{p[8:]}"; return self._send(open(f, "rb").read(), "text/css" if f.endswith(".css") else "application/javascript")
        if p.startswith("/api/assets/"):
            _, _, _, brand, name = p.split("/"); return self._send(open(f"{ASSETS}/{brand}/{name}", "rb").read(), "image/svg+xml")
        m = {"/api/bootstrap": "bootstrap", "/api/analytics": "analytics", "/api/decisions": "decisions", "/api/live-context": "live"}
        return self._send(open(f"{FX}/{m[p]}.json", "rb").read(), "application/json")
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        return self._send(open(f"{FX}/generate.json", "rb").read(), "application/json")
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
