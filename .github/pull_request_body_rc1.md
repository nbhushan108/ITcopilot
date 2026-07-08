## Summary

This PR merges **ITcopilot Module 1 — Repository Foundation** as the `v0.1.0-rc1` release candidate.

- FastAPI backend with tax computation, health probes, and JWT auth skeleton
- Six domain packages: `tax_engine`, `parsers`, `broker_imports`, `excel_engine`, `reporting`, `common`
- React + TypeScript + Vite frontend dashboard
- **101 tests** at **96%+ coverage** (95% CI floor)
- CI: ruff, mypy, bandit, **pip-audit** (zero known vulnerabilities), frontend lint/build
- Production Docker entrypoint with Alembic migrations
- PyJWT (HS256) replaces python-jose — removes transitive `ecdsa` CVE

## Test plan

- [ ] GitHub Actions CI passes on this PR
- [ ] `pytest` passes locally with coverage ≥ 95%
- [ ] `pip-audit` reports no known vulnerabilities
- [ ] `npm audit` reports 0 vulnerabilities in `apps/web`
- [ ] Docker Compose dev stack starts: `docker compose up --build`
- [ ] Production secrets generated via `python scripts/generate_production_secrets.py`
- [ ] API health: `GET /api/v1/health/live` and `/api/v1/health/ready`
- [ ] Tax compute smoke test: `POST /api/v1/tax/compute`

## Notes

Replaces the GitHub initial README-only commit on `main` with the full project scaffold.
