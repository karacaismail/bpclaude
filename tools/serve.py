#!/usr/bin/env python3
"""Yerel önizleme sunucusu: docs/ klasörünü GitHub Pages'teki gibi /bpclaude/ yolu altında sunar.
Bulunmayan adreslerde docs/404.html dosyasını 404 durumuyla döndürür; böylece yerel testler yayındaki davranışı görür.
Kullanım: python3 tools/serve.py [port]   (varsayılan 4173, yalnız 127.0.0.1)"""
import http.server, os, posixpath, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DOCS_REAL = os.path.realpath(DOCS)
PREFIX = "/bpclaude/"


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _target(self):
        path = urllib.parse.urlsplit(self.path).path
        if not path.startswith(PREFIX):
            return None
        rel = urllib.parse.unquote(path[len(PREFIX):]).lstrip("/")
        full = os.path.realpath(os.path.join(DOCS, posixpath.normpath(rel) if rel else "."))
        # Çözülmüş yol docs/ dışına çıkıyorsa (mutlak yol, "..", sembolik bağ) dosya sunulmaz.
        if os.path.commonpath([full, DOCS_REAL]) != DOCS_REAL:
            return None
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        return full if os.path.isfile(full) else None

    def _host_ok(self):
        host = (self.headers.get("Host") or "").lower()
        return host in ("127.0.0.1:%d" % self.server.server_port, "localhost:%d" % self.server.server_port)

    def do_GET(self):
        self._serve(True)

    def do_HEAD(self):
        self._serve(False)

    def _serve(self, body):
        if not self._host_ok():
            self.send_error(421, "Misdirected Request")
            return
        path = urllib.parse.urlsplit(self.path).path
        if path in ("/", PREFIX.rstrip("/")):
            self.send_response(302)
            self.send_header("Location", PREFIX)
            self.end_headers()
            return
        full = self._target()
        status = 200
        if full is None:
            full = os.path.join(DOCS, "404.html")
            status = 404
            if not os.path.isfile(full):
                self.send_error(404)
                return
        data = open(full, "rb").read()
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(full) + ("; charset=utf-8" if full.endswith((".html", ".css", ".js", ".json", ".csv", ".txt")) else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if body:
            self.wfile.write(data)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("http://127.0.0.1:%d%s" % (port, PREFIX), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
