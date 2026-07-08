# syntax=docker/dockerfile:1

# =============================================================================
# ITcopilot API - Multi-stage Docker Build
# =============================================================================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Development Stage
# =============================================================================
FROM base AS development

COPY pyproject.toml README.md ./
COPY apps/api/app ./apps/api/app
COPY packages ./packages

RUN pip install --upgrade "pip>=26.1.2" && \
    pip install -e ".[dev]"

RUN mkdir -p /app/data /app/logs /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--app-dir", "apps/api"]

# =============================================================================
# Production Builder
# =============================================================================
FROM base AS builder

COPY pyproject.toml README.md ./
COPY apps/api/app ./apps/api/app
COPY packages ./packages

RUN pip install --upgrade "pip>=26.1.2" && \
    pip install -e .

# =============================================================================
# Production Stage
# =============================================================================
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 itcopilot \
    && useradd --uid 1000 --gid itcopilot --shell /bin/bash --create-home itcopilot

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY apps/api/app ./apps/api/app
COPY apps/api/alembic ./apps/api/alembic
COPY packages ./packages
COPY alembic.ini pyproject.toml README.md ./
COPY docker/entrypoint.sh /entrypoint.sh

RUN mkdir -p /app/data /app/logs /app/uploads && \
    chmod +x /entrypoint.sh && \
    chown -R itcopilot:itcopilot /app

USER itcopilot

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--app-dir", "apps/api"]
