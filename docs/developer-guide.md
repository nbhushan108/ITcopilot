# Developer Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional)
- Git

## Local Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/nbhushan108/ITcopilot.git
cd itcopilot

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
pre-commit install
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 3. Initialize Database

**Development / Testing** (auto-create enabled by default):

```bash
python scripts/init_db.py
```

**Production** (Alembic migrations only):

```bash
# Set AUTO_CREATE_SCHEMA=false in .env
alembic upgrade head
```

Never use `create_all()` in production. The `AUTO_CREATE_SCHEMA` setting controls startup behavior.

### 4. Start API Server

```bash
python scripts/dev_server.py
# Or directly:
cd apps/api && uvicorn app.main:app --reload --app-dir .
```

API available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Liveness: http://localhost:8000/api/v1/health/live
- Readiness: http://localhost:8000/api/v1/health/ready

### Authentication

Development defaults (`AUTH_ENABLED=false`):
- Tax endpoints work without a token in development/testing.

Production (`AUTH_ENABLED=true`, enforced automatically):
- Obtain a token: `POST /api/v1/auth/token` with `{"username":"admin","password":"secret"}`
- Pass `Authorization: Bearer <token>` on protected routes.

Generate a secure `SECRET_KEY` for production:

```bash
openssl rand -hex 32
```

### 5. Start Frontend

```bash
cd apps/web
npm install
npm run dev
```

Frontend available at http://localhost:5173

## Docker Development

```bash
docker compose up --build
```

Services:
- API: http://localhost:8000
- Web: http://localhost:5173
- PostgreSQL: localhost:5432

## Running Tests

```bash
# Full test suite with coverage
pytest

# Specific test file
pytest apps/api/tests/test_health.py -v

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration
```

## Code Quality

```bash
# Lint
ruff check apps packages scripts tests

# Format
ruff format apps packages scripts tests

# Type check
mypy apps/api/app packages

# Security scan
bandit -r apps/api/app packages
```

## Project Structure

```
ITcopilot/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # React frontend
├── packages/
│   ├── common/       # Shared utilities
│   ├── tax_engine/   # Tax computation
│   ├── parsers/      # Document parsers
│   ├── broker_imports/
│   ├── excel_engine/
│   └── reporting/
├── docs/             # MkDocs documentation
├── scripts/          # Utility scripts
├── sample_data/      # Test data
├── tests/            # Package-level tests
└── docker/           # Docker configs
```

## Adding a New Broker Importer

1. Create `packages/broker_imports/my_broker.py` extending `BaseBrokerImporter`
2. Implement `broker_name` property and `import_statement()` method
3. Register in `packages/broker_imports/registry.py`
4. Add tests and sample data

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations (production)
alembic upgrade head

# Rollback
alembic downgrade -1
```

In production, set `AUTO_CREATE_SCHEMA=false` and apply migrations via Alembic before deployment.

## Environment Profiles

See the [Configuration Guide](configuration-guide.md) for the full variable reference.

| Variable | Development | Testing | Production |
|----------|-------------|---------|------------|
| `ENVIRONMENT` | development | testing | production |
| `DEBUG` | true | true | false |
| `DATABASE_URL` | sqlite | in-memory | postgresql |
| `AUTO_CREATE_SCHEMA` | true | true | false |
| `AUTH_ENABLED` | false | false | true (forced) |
| `JWT_SECRET` | optional | optional | required (or `SECRET_KEY`) |
| `LOG_JSON` | false | false | true |
| `ENABLE_AI` | false | false | false |
| `ENABLE_CACHE` | false | false | false |
| `AUTH_ADMIN_PASSWORD` | secret (dev) | secret | not used |
| `AUTH_ADMIN_PASSWORD_HASH` | — | — | required |
| `LOG_LEVEL` | DEBUG | INFO | INFO |
