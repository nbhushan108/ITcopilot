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
        COMMON[common]
    end

    subgraph Infrastructure
        DB[(SQLite / PostgreSQL)]
        LOG[Loguru Logging]
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
    TAX --> COMMON
    PARSE --> COMMON
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
| `common` | Shared types, constants, validators |
| `tax_engine` | Income tax computation (old/new regime) |
| `parsers` | PDF, CSV document parsing |
| `broker_imports` | Broker statement import adapters |
| `excel_engine` | Excel read/write operations |
| `reporting` | Tax report generation |

### Infrastructure

- **Database**: SQLAlchemy 2 async with SQLite (dev) / PostgreSQL (prod)
- **Logging**: Loguru with console and rotating file handlers
- **Configuration**: pydantic-settings with environment-based profiles

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
