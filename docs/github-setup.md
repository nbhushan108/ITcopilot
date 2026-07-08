# GitHub Repository Setup (RC1)

Before publishing `v0.1.0-rc1`, complete these steps:

## 1. Create the GitHub repository

1. Create a new public repository (suggested name: `itcopilot`).
2. Update `pyproject.toml` `[project.urls]` if your org/name differs.
3. Update `mkdocs.yml` `repo_url` and `site_url` for your GitHub Pages site.

## 2. Security reporting

Primary channel: **GitHub Security Advisories** (Repository → Security → Advisories → Report a vulnerability).

Optional email contact can be added once a domain is verified.

## 3. Production deployment secrets

```bash
python scripts/generate_production_secrets.py
```

Copy output into `.env` (never commit) or export for Docker Compose:

```bash
export SECRET_KEY="..."
export AUTH_ADMIN_PASSWORD_HASH="..."
docker compose --profile production up --build
```

## 4. Tag RC1

```bash
git tag -a v0.1.0-rc1 -m "ITcopilot v0.1.0-rc1"
git push origin v0.1.0-rc1
```

## 5. Verify CI

Confirm the GitHub Actions `CI` workflow is green on `main` before announcing the release.
