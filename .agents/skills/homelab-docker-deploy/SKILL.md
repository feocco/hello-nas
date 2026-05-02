---
name: homelab-docker-deploy
description: "Example skill for adding, updating, or troubleshooting deployment of a Dockerized service to a homelab NAS. The pattern keeps app source, image publishing, and private runtime Compose config separate."
---

# Homelab Docker Deploy

## Core Rule

Keep application code and runtime configuration separate.

- App repos own source code, Dockerfile, tests, and container image publishing.
- A private homelab config repo owns NAS runtime config, service folders, Compose files, and deploy orchestration.
- Never commit real secrets. Use `.env.example` in git and runtime `.env` files on the NAS.

## Workflow

1. Inspect the app repo.
   - Identify the service name, startup command, exposed port, persistent data path, required env vars, and required config files.
   - Prefer `ghcr.io/<owner>/<service>:latest` unless the user asks for a different image name.
   - If the app repo already has Docker and GHCR publishing, update instead of replacing.

2. Prepare the app repo image.
   - Add or update `Dockerfile`.
   - Add or update `.github/workflows/container.yml`; use `assets/container-ghcr.yml` as the baseline.
   - Keep runtime secrets and local config out of the app repo with `.gitignore`.
   - Run app tests and a local Docker build when feasible.
   - Commit and push the app repo so the registry receives a fresh image.

3. Register the service in the private homelab config repo.
   - Create one service folder per deployable service, for example `my-service/docker-compose.yml`.
   - Use `assets/docker-compose.service.yml` as the baseline.
   - Add `.env.example`; do not add real `.env`.
   - Add config files only when they belong in the private homelab config repo.
   - Add `data/.gitkeep` for persistent state directories, not real runtime data.
   - Add the service to `services.yaml`:

```yaml
services:
  my-service:
    path: my-service
    enabled: true
```

4. Validate locally before pushing homelab config.
   - Run the deploy tooling tests.
   - List enabled services.
   - Run a dry-run deploy for the target service.

5. Push and verify the NAS deployment.
   - Push the homelab config repo's main branch.
   - Watch the deploy workflow.
   - Inspect the deploy log and confirm it deploys the intended service from the NAS runtime path.
   - Confirm the container is running and the app's health endpoint responds.

## Deployment Facts To Customize

- GitHub owner or organization.
- Private homelab config repository name.
- Local checkout path for the private homelab config repo.
- NAS runtime config path.
- Self-hosted runner labels.
- Compose version available on the NAS.

## Guardrails

- Do not put service runtime config in the public app repo unless it is intentionally generic.
- Do not overwrite `.env` or `data/` on the NAS.
- Do not make one giant Compose file unless services are tightly coupled.
- For public images, no NAS registry login is usually needed.
- For private images, confirm the NAS has package read access.
- Keep deploy scripts portable across local shells, NAS shells, and runner containers.
- When SSH access works, prefer non-interactive checks and avoid asking for passwords or tokens in chat.

## References

- Read `references/homelab-pattern.md` when exact commands, file layout, or troubleshooting details are needed.
- Copy and adapt `assets/container-ghcr.yml` for app repo GHCR publishing.
- Copy and adapt `assets/docker-compose.service.yml` for a new homelab service folder.
- Copy and adapt `assets/env.example` for service env documentation.

