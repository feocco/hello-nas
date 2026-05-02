# Homelab Pattern

## Standard Shape

```text
app repo
  Dockerfile
  .github/workflows/container.yml
  source code

private homelab config repo
  services.yaml
  <service>/
    docker-compose.yml
    .env.example
    data/.gitkeep
```

Flow:

1. App repo pushes `ghcr.io/<owner>/<service>:latest`.
2. The private homelab config repo declares the runtime Compose project.
3. Push to the homelab config repo triggers a NAS runner.
4. Runner syncs files to the NAS runtime path, preserving runtime `.env` and `data/`.
5. Runner calls the deploy script for changed services.

## Homelab Commands

Customize these for your environment:

```bash
cd /path/to/homelab-config
./scripts/test-deploy-tooling
./scripts/homelab-deploy --list --base-dir /path/to/homelab-config
./scripts/homelab-deploy <service> --dry-run --base-dir /path/to/homelab-config --deploy-base-dir /path/to/homelab-config
```

After pushing:

```bash
gh run list --repo <owner>/<homelab-config-repo> --workflow Deploy --limit 3
gh run watch <run-id> --repo <owner>/<homelab-config-repo> --exit-status
gh run view <run-id> --repo <owner>/<homelab-config-repo> --log
```

If SSH is configured:

```bash
ssh -o BatchMode=yes <user>@<nas-host> 'docker ps --filter name=<service>'
ssh -o BatchMode=yes <user>@<nas-host> 'docker logs --tail=100 <service>'
```

## services.yaml

`services.yaml` is the deploy whitelist. A service deploys only when it is enabled and the changed files include either `services.yaml` or files under that service path.

```yaml
services:
  my-service:
    path: my-service
    enabled: true
```

## Runtime Config

Public app repos should contain only generic examples. Private homelab config repos may contain reviewed non-secret runtime config when useful. Real tokens and passwords still belong in runtime `.env` files, not git.

The deploy workflow should exclude runtime secrets and persistent data, for example:

```text
./.git
./*/.env
./*/data
```

## Troubleshooting

- `No enabled services to deploy.` after a service-folder change usually means `services.yaml` parsing failed, the path does not match the changed directory, or the workflow is checking the wrong base directory.
- `executable file not found in $PATH` usually means the app image `CMD` or Compose `command` points to the wrong CLI entry point.
- Docker permission errors inside the runner usually mean the runner lacks Docker socket access or the workflow is running Docker outside the approved deploy path.
- NAS Compose versions can lag behind desktop Docker, so keep Compose files conservative.
- Runner container shell tools can differ from your local shell; avoid fragile shell features in deploy scripts.

