# Architecture

## System Overview

ITcopilot follows clean architecture principles with clear separation between API, domain packages, and infrastructure.

```mermaid
graph TB
    subgraph Client Layer
        WEB[React Web App]
        CLI[Scripts / CLI]
    end

    subgraph API Layer
        FAST[FastAPI Application]
        ROUTERS[Routers]
        SERVICES[Services]
        SCHEMAS[Pydantic Schemas]
    end

    subgraph Domain Packages
        TAX[tax_engine]
        PARSE[parsers]
        BROKER[broker_imports]
        EXCEL[excel_engine]
        REPORT[reporting]
        CONFIG[common/config]
    end

    subgraph Infrastructure
        DB[(SQLite / PostgreSQL)]
        LOG[Loguru Logging]
        ENV[Environment Profiles]
        DOCKER[Docker]
    end

    WEB --> FAST
    CLI --> FAST
    FAST --> ROUTERS
    ROUTERS --> SERVICES
    SERVICES --> SCHEMAS
    SERVICES --> TAX
    SERVICES --> BROKER
    SERVICES --> REPORT
    TAX --> CONFIG
    PARSE --> CONFIG
    FAST --> CONFIG
    CONFIG --> ENV
    BROKER --> PARSE
    REPORT --> EXCEL
    REPORT --> TAX
    SERVICES --> DB
    FAST --> LOG
```

## Layer Responsibilities

### API Layer (`apps/api`)

- HTTP request handling and routing
- Input validation via Pydantic schemas
- Dependency injection for services and database sessions
- Exception handling and structured error responses

### Domain Packages (`packages/`)

| Package | Responsibility |
|---------|---------------|
| `common` | Shared types, constants, validators, **configuration engine** |
| `tax_engine` | Income tax computation (old/new regime) |
| `parsers` | PDF, CSV document parsing |
| `broker_imports` | Broker statement import adapters |
| `excel_engine` | Excel read/write operations |
| `reporting` | Tax report generation |

### Infrastructure

- **Database**: SQLAlchemy 2 async with SQLite (dev) / PostgreSQL (prod)
- **Logging**: Loguru with colored console, daily rotation, JSON file logs
- **Configuration**: `packages/common/config/` — pydantic-settings profiles, tax config, feature flags, metadata

See the [Configuration Guide](configuration-guide.md) for full details.

## Configuration Engine (Module 2)

```mermaid
graph LR
    ENV[.env profiles] --> SETTINGS[Settings Loader]
    SETTINGS --> API[FastAPI App]
    SETTINGS --> TAX_CFG[TaxYearConfiguration]
    SETTINGS --> FLAGS[FeatureFlags]
    SETTINGS --> META[ApplicationMetadata]
    SETTINGS --> LOG[Loguru]
```

The configuration engine provides:

- `DevelopmentSettings`, `TestingSettings`, `ProductionSettings`
- Automatic environment detection via `ENVIRONMENT`
- Singleton loader: `get_settings()`
- Multi-year tax configuration registry
- Runtime feature flags for all optional modules
- Validated secrets, hosts, ports, and tax defaults

## Design Principles

1. **Dependency Injection** — FastAPI `Depends()` for settings, DB sessions, services
2. **SOLID** — Single-responsibility services, interface-based parsers/importers
3. **Typed Python** — 100% type hints with strict MyPy
4. **Domain-Driven Design** — Tax computation logic isolated in `tax_engine` package

## Data Flow: Tax Computation

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant TaxService
    participant TaxCalculator
    participant Database

    Client->>Router: POST /api/v1/tax/compute
    Router->>TaxService: compute_tax(request)
    TaxService->>TaxCalculator: compute(income, regime)
    TaxCalculator-->>TaxService: TaxComputationResult
    TaxService->>Database: persist assessment
    Database-->>TaxService: TaxAssessment
    TaxService-->>Router: TaxAssessmentResponse
    Router-->>Client: 201 Created
```

## Deployment Architecture

```mermaid
graph LR
    subgraph Docker Compose
        NGINX[Nginx / Web]
        API[FastAPI API]
        PG[(PostgreSQL)]
    end

    NGINX --> API
    API --> PG
```

Production deployments use multi-stage Docker builds with non-root user, health checks, and PostgreSQL.
