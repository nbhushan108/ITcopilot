# Changelog

All notable changes to ITcopilot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-rc1] - 2026-07-08

### Added
- JWT authentication skeleton with `/api/v1/auth/token` endpoint
- Production `AUTH_ADMIN_PASSWORD_HASH` requirement for token issuance
- Repository layer for tax assessments
- Liveness (`/health/live`) and readiness (`/health/ready`) probes with DB check
- Package smoke tests for parsers, broker imports, excel engine, reporting
- GitHub issue/PR templates and Dependabot configuration
- ESLint configuration for frontend
- `py.typed` markers for typed packages
- 95% CI coverage floor
- Production secrets generator script (`scripts/generate_production_secrets.py`)
- Comprehensive test suite (101 tests, 96%+ coverage)
- GitHub setup guide for RC1 publication
- Vite 6 upgrade (npm audit clean)
- Docker production entrypoint with Alembic migrations

### Changed
- Production uses Alembic-only migrations (`AUTO_CREATE_SCHEMA=false`)
- Zerodha importer routes CSV parsing through parser registry
- Tightened CORS defaults for production
- Removed unused dependencies (pandas, pymupdf, orjson, passlib)
- Production Docker compose requires `SECRET_KEY` and `AUTH_ADMIN_PASSWORD_HASH`

### Fixed
- Replaced `python-jose` with `PyJWT` to remove transitive `ecdsa` vulnerability (PYSEC-2026-1325)
- Added `pip-audit` to CI; upgraded pip to >=26.1.2 in CI and Docker builds
- Missing FastAPI/Request imports in exception handlers
- Frontend package-lock.json regeneration
- Bandit CI failures (documented skips for container bind and dev auth)
- Ruff format check failures

## [0.1.0] - 2025-07-08

### Added

- FastAPI backend with health, version, and tax computation endpoints
- Income tax engine supporting old and new tax regimes
- SQLAlchemy 2 async database layer with SQLite and PostgreSQL support
- PDF and CSV document parsers with registry pattern
- Zerodha broker statement importer
- Excel report generation engine
- Tax report generator with ITR summary template
- React + TypeScript + Vite + Tailwind frontend dashboard
- Docker multi-stage builds for development and production
- Docker Compose with API, web, and PostgreSQL services
- GitHub Actions CI pipeline (lint, type check, test, security scan)
- GitHub Actions release pipeline with Docker image publishing
- CodeQL security analysis workflow
- Pre-commit hooks (ruff, mypy, bandit)
- MkDocs Material documentation
- Comprehensive test suite with pytest and coverage
- Sample data for broker imports and tax computation

[Unreleased]: https://github.com/nbhushan108/ITcopilot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nbhushan108/ITcopilot/releases/tag/v0.1.0
