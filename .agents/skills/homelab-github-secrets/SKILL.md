---
name: homelab-github-secrets
description: "Example skill for adding, updating, validating, or troubleshooting runtime environment variables and GitHub Actions secrets for a homelab deployment workflow. Use when a service needs .env values, .env.example contracts, service-secrets.yaml manifests, gh secret set uploads, generated deploy workflow secret mappings, or rendered NAS runtime .env files."
---

# Homelab GitHub Secrets

## Core Rule

Keep secret values out of git, but keep the secret contract in git.

- `.env.example` documents the runtime keys a service expects.
- `service-secrets.yaml` is the source of truth for which keys are managed through GitHub Actions secrets.
- Ignored service `.env` files contain local values used to upload/update GitHub secrets.
- GitHub Actions secrets store the real values centrally.
- The deploy workflow renders NAS runtime `.env` files from GitHub secrets before Compose starts.

Use this skill alongside `homelab-docker-deploy`: deployment config should not be considered ready until required secrets are uploaded and render validation passes.

## Workflow

1. Work in the private homelab config repo.
2. Confirm the service exists in `services.yaml` and has `<service>/.env.example`.
3. Add or update `service-secrets.yaml`:

```yaml
services:
  my-service:
    env:
      - API_KEY
      - SERVICE_PORT
```

4. Ensure the ignored local `<service>/.env` exists and contains real values for every key in the manifest.
5. Run the helper scripts:

```bash
./scripts/set-service-secrets <service> --repo <owner>/<homelab-config-repo>
./scripts/generate-service-secret-workflow-env
./scripts/check-service-secrets
./scripts/test-deploy-tooling
```

6. Commit `service-secrets.yaml`, generated workflow changes, and script/config changes. Never commit `<service>/.env`.
7. Push the homelab config repo, watch the deploy workflow, and validate runtime values without printing secret values.

For a secret-value-only update where no config commit is needed, run:

```bash
./scripts/set-service-secrets <service> --repo <owner>/<homelab-config-repo> --dispatch
```

This uploads ignored local `.env` values and dispatches the deploy workflow with `force_recreate=true` for that service.

## Naming Convention

Use service-prefixed GitHub secret names:

```text
<SERVICE_PREFIX>__<ENV_KEY>
```

Examples:

- `hello-nas` + `HELLO_NAS_MESSAGE` -> `HELLO_NAS__HELLO_NAS_MESSAGE`
- `my-service` + `API_KEY` -> `MY_SERVICE__API_KEY`

The app/container still receives the plain env key (`API_KEY`), because `render-service-env` maps the prefixed GitHub secret back into `<service>/.env`.

## Scripts

Prefer repo scripts over hand-editing.

- `scripts/set-service-secrets <service> --repo <owner>/<repo>`: reads ignored `<service>/.env` and uploads values to GitHub Actions secrets.
- `scripts/set-service-secrets <service> --repo <owner>/<repo> --dispatch`: uploads values and runs the deploy workflow with `force_recreate=true`.
- `scripts/generate-service-secret-workflow-env`: regenerates the marked `env:` block in `.github/workflows/deploy.yml` from `service-secrets.yaml`.
- `scripts/render-service-env --all`: used by the deploy workflow to write NAS runtime `.env` files.
- `scripts/check-service-secrets`: verifies manifest, `.env.example`, and generated workflow mappings are in sync.

If `service-secrets.yaml` changes, always regenerate and check the workflow env block before committing.

## Validation

Use non-secret validation by checking presence, permissions, and hashes. Do not print real secret values in chat or logs.

Useful NAS-side validation pattern:

```bash
file_hash=$(sudo awk -F= '$1=="MY_KEY"{sub(/^[^=]*=/,""); printf "%s",$0}' /path/to/runtime/my-service/.env | sha256sum | awk '{print $1}')
container_hash=$(sudo docker exec my-service sh -c 'printf "%s" "$MY_KEY" | sha256sum' | awk '{print $1}')
test "$file_hash" = "$container_hash" && echo "MY_KEY matches runtime .env"
```

Also check:

```bash
sudo stat -c "%a %n" /path/to/runtime/my-service/.env
```

Expected mode is `600`.

## Guardrails

- Do not commit real `.env` files.
- Do not print secret values to prove validation.
- Do not rely on scripts to dynamically fetch arbitrary GitHub secrets during a workflow run; GitHub requires secret references to appear in workflow YAML before the job starts.
- Use `generate-service-secret-workflow-env` to maintain those explicit workflow references programmatically.
- Treat `service-secrets.yaml` and `.env.example` drift as a deploy blocker.

