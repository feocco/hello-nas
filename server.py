from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os


MESSAGE = "Hello NAS"


class Handler(BaseHTTPRequestHandler):
    server_version = "hello-nas/1.0"

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "ok", "service": "hello-nas"})
            return

        if self.path not in ("/", "/index.html"):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{MESSAGE}</title>
    <style>
      :root {{
        color-scheme: light dark;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      body {{
        min-height: 100vh;
        margin: 0;
        display: grid;
        place-items: center;
        background: #f5f7fb;
        color: #172033;
      }}
      main {{
        text-align: center;
      }}
      h1 {{
        margin: 0 0 0.5rem;
        font-size: clamp(2.5rem, 8vw, 5.5rem);
        letter-spacing: 0;
      }}
      p {{
        margin: 0;
        font-size: 1.125rem;
        color: #536078;
      }}
      @media (prefers-color-scheme: dark) {{
        body {{
          background: #111827;
          color: #f8fafc;
        }}
        p {{
          color: #cbd5e1;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>{MESSAGE}</h1>
      <p>Deployed from GHCR to the NAS.</p>
    </main>
  </body>
</html>
"""
        self._send_bytes(body.encode("utf-8"), "text/html; charset=utf-8")

    def log_message(self, fmt, *args):
        print("%s - - %s" % (self.address_string(), fmt % args), flush=True)

    def _send_json(self, payload):
        self._send_bytes(
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            "application/json",
        )

    def _send_bytes(self, body, content_type):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    host = os.environ.get("SERVICE_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVICE_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"hello-nas listening on {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

