# hello-nas

`hello-nas` is a small Python web server used to test a Docker-based homelab
runner deploy workflow.

## Demo App

The server uses only the Python standard library:

- `GET /` shows a simple `Hello NAS` page.
- `GET /health` returns `{"status":"ok","service":"hello-nas"}`.

The container image is published with GitHub Actions:

```text
ghcr.io/feocco/hello-nas:latest
```

## Codex Skill Example

The [homelab-docker-deploy skill](.agents/skills/homelab-docker-deploy)
directory contains a sanitized example Codex skill for this style of deployment
workflow.

See the [homelab pattern reference](.agents/skills/homelab-docker-deploy/references/homelab-pattern.md)
for the system pattern behind the example.

It is included for reference, not as production-ready configuration. Replace the
placeholder owner, repository, host, and path values before adapting it.

## Local

```bash
python3 -m unittest
SERVICE_PORT=8080 python3 server.py
```

Then open `http://localhost:8080`.
