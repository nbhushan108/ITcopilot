# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

When `AUTH_ENABLED=true` (forced in production), protected endpoints require a Bearer JWT token.

Obtain a token via `POST /auth/token`:
- **Development/testing:** use `AUTH_ADMIN_PASSWORD` (defaults to `secret` when unset)
- **Production:** requires `AUTH_ADMIN_PASSWORD_HASH` (bcrypt hash)

When `AUTH_ENABLED=false`, protected routes accept requests without a token.

## Endpoints

### Health

#### GET /health

Returns readiness status including database connectivity.

**Response 200:**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-08T10:30:00Z",
  "environment": "development",
  "version": "0.1.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Connected"
    }
  }
}
```

#### GET /health/live

Returns liveness probe (process running).

#### GET /health/ready

Returns readiness probe with database connectivity check.

#### GET /version

Returns application version information.

**Response 200:**

```json
{
  "name": "ITcopilot",
  "version": "0.1.0",
  "api_prefix": "/api/v1",
  "environment": "development"
}
```

### Authentication

#### POST /auth/token

Obtain a JWT access token.

**Request Body:**

```json
{
  "username": "admin",
  "password": "secret"
}
```

**Response 200:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in_minutes": 30
}
```

Protected endpoints require `Authorization: Bearer <token>` when `AUTH_ENABLED=true`.

### Tax

#### POST /tax/compute

Compute income tax and persist assessment.

**Request Body:**

```json
{
  "pan": "ABCDE1234F",
  "assessment_year": "2025-26",
  "regime": "old",
  "gross_salary": "1500000",
  "other_income": "75000",
  "section_80c": "150000",
  "section_80d": "25000",
  "hra_exemption": "120000",
  "standard_deduction": "50000"
}
```

**Response 201:**

```json
{
  "id": "uuid",
  "pan": "ABCDE1234F",
  "assessment_year": "2025-26",
  "regime": "old",
  "gross_total_income": "1575000.00",
  "total_deductions": "345000.00",
  "taxable_income": "1230000.00",
  "tax_payable": "165000.00",
  "notes": "Computed via old regime for AY 2025-26",
  "created_at": "2025-07-08T10:30:00Z",
  "updated_at": "2025-07-08T10:30:00Z"
}
```

#### GET /tax/assessments/{assessment_id}

Retrieve a tax assessment by ID.

#### GET /tax/assessments

List tax assessments with optional filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pan` | string | Filter by PAN |
| `limit` | int | Max records (default 50) |
| `offset` | int | Pagination offset |

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "NotFoundError",
  "message": "Tax assessment not found: uuid",
  "details": {}
}
```

| Status | Error Type | Description |
|--------|-----------|-------------|
| 400 | ITcopilotError | General application error |
| 401 | AuthenticationError | Authentication failed |
| 403 | AuthorizationError | Insufficient permissions |
| 404 | NotFoundError | Resource not found |
| 422 | ValidationError | Input validation failed |
| 500 | InternalServerError | Unexpected server error |

## Interactive Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
