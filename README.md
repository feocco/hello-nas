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

## Homelab SRE

The `Homelab SRE Investigate` workflow runs from `repository_dispatch` events
sent by `homelab-sre-agent`. It expects these repository secrets:

- `OPENAI_API_KEY`: lets `openai/codex-action` run the investigation.
- `SRE_GITHUB_TOKEN`: lets the workflow push the Codex branch and open a draft
  PR.

Use `.env.sre.example` as the local template for uploading those secret names.

## Codex Skill Example

The [.agents/skills](.agents/skills) directory contains sanitized example Codex
skills used by this deployment workflow:

- [homelab-docker-deploy](.agents/skills/homelab-docker-deploy)
- [homelab-github-secrets](.agents/skills/homelab-github-secrets)

See the [homelab pattern reference](.agents/skills/homelab-docker-deploy/references/homelab-pattern.md)
and [secrets pattern reference](.agents/skills/homelab-github-secrets/references/pattern.md)
for the system patterns behind the example.

It is included for reference, not as production-ready configuration. Replace the
placeholder owner, repository, host, and path values before adapting it.

## Local

```bash
python3 -m unittest
SERVICE_PORT=8080 python3 server.py
```

Then open `http://localhost:8080`.
