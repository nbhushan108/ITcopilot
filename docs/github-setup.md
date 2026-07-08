# GitHub Repository Setup (RC1)

Repository: **https://github.com/nbhushan108/ITcopilot**

## 1. Clone and develop

```bash
git clone https://github.com/nbhushan108/ITcopilot.git
cd ITcopilot
python -m venv .venv
pip install -e ".[dev]"
pre-commit install
pytest
```

## 2. Security reporting

Primary channel: [GitHub Security Advisories](https://github.com/nbhushan108/ITcopilot/security/advisories/new).

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

## 4. Release workflow

```bash
# After CI is green on main
git tag -a v0.1.0-rc1 -m "ITcopilot v0.1.0-rc1"
git push origin v0.1.0-rc1
```

## 5. Verify CI

Confirm the GitHub Actions `CI` workflow is green on `main` before announcing the release.
