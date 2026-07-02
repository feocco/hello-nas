from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import json
import os


DEFAULT_MESSAGE = "Hello NAS"
MESSAGE_ENV = "HELLO_NAS_MESSAGE"
CANARY_STATUS = "ok"


def openapi_document():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Hello NAS",
            "version": "1.0.0",
            "description": "Deployment smoke test service for the homelab runtime.",
        },
        "paths": {
            "/": {
                "get": {
                    "summary": "Show the smoke test landing page",
                    "responses": {
                        "200": {
                            "description": "HTML landing page",
                            "content": {"text/html": {"schema": {"type": "string"}}},
                        }
                    },
                }
            },
            "/health": {
                "get": {
                    "summary": "Report service health",
                    "responses": {
                        "200": {
                            "description": "Service health payload",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["status", "service", "message_configured"],
                                        "properties": {
                                            "status": {"type": "string", "const": "ok"},
                                            "service": {"type": "string", "const": "hello-nas"},
                                            "message_configured": {"type": "boolean"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/canary-error": {
                "get": {
                    "summary": "Exercise canary error logging",
                    "description": "Intentional smoke endpoint used to verify log and SRE alert plumbing.",
                    "responses": {
                        "200": {
                            "description": "Canary status payload",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["status"],
                                        "properties": {"status": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    },
                }
            },
        },
    }


def docs_html():
    page_message = escape(message())
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hello NAS API</title>
    <style>
      :root {{
        color-scheme: light dark;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f6f7f9;
        color: #18202f;
      }}
      body {{ margin: 0; }}
      main {{
        max-width: 920px;
        margin: 0 auto;
        padding: 48px 20px 64px;
      }}
      h1 {{ margin: 0 0 8px; font-size: 2.25rem; letter-spacing: 0; }}
      h2 {{ margin-top: 32px; font-size: 1.15rem; }}
      p {{ line-height: 1.55; color: #4b5563; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: #ffffff; }}
      th, td {{ padding: 12px; border-bottom: 1px solid #d8dee8; text-align: left; vertical-align: top; }}
      th {{ color: #1f2937; font-size: 0.85rem; text-transform: uppercase; }}
      code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
      a {{ color: #075985; }}
      .status {{ display: inline-flex; gap: 8px; align-items: center; font-weight: 600; }}
      .dot {{ width: 10px; height: 10px; border-radius: 50%; background: #16a34a; }}
      @media (prefers-color-scheme: dark) {{
        :root {{ background: #101622; color: #f8fafc; }}
        p {{ color: #cbd5e1; }}
        table {{ background: #172033; }}
        th, td {{ border-bottom-color: #334155; }}
        th {{ color: #e2e8f0; }}
        a {{ color: #7dd3fc; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Hello NAS</h1>
      <p>Deployment smoke test service for the homelab runtime. Current message: <strong>{page_message}</strong>.</p>
      <p class="status"><span class="dot"></span> Healthy when <a href="/health">/health</a> returns <code>status: ok</code>.</p>
      <h2>API Endpoints</h2>
      <table>
        <thead><tr><th>Method</th><th>Path</th><th>Purpose</th><th>Auth</th></tr></thead>
        <tbody>
          <tr><td><code>GET</code></td><td><a href="/"><code>/</code></a></td><td>Smoke test landing page.</td><td>None</td></tr>
          <tr><td><code>GET</code></td><td><a href="/health"><code>/health</code></a></td><td>Machine-readable health check.</td><td>None</td></tr>
          <tr><td><code>GET</code></td><td><a href="/canary-error"><code>/canary-error</code></a></td><td>Canary log/error plumbing check.</td><td>None</td></tr>
        </tbody>
      </table>
      <h2>Machine Schema</h2>
      <p><a href="/openapi.json">OpenAPI JSON</a></p>
    </main>
  </body>
</html>
"""


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def message():
    return os.environ.get(MESSAGE_ENV, DEFAULT_MESSAGE)


class Handler(BaseHTTPRequestHandler):
    server_version = "hello-nas/1.0"

    def do_GET(self):
        if self.path == "/health":
            self._send_json(
                {
                    "status": "ok",
                    "service": "hello-nas",
                    "message_configured": MESSAGE_ENV in os.environ,
                }
            )
            return

        if self.path == "/openapi.json":
            self._send_json(openapi_document())
            return

        if self.path == "/docs":
            self._send_bytes(docs_html().encode("utf-8"), "text/html; charset=utf-8")
            return

        if self.path == "/canary-error":
            print("ERROR hello-nas canary failure: intentional canary log event", flush=True)
            self._send_json({"status": CANARY_STATUS})
            return

        if self.path not in ("/", "/index.html"):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        page_message = escape(message())
        body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page_message}</title>
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
      <h1>{page_message}</h1>
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
    load_dotenv()
    host = os.environ.get("SERVICE_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVICE_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"hello-nas listening on {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
