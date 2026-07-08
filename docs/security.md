# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in ITcopilot, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Report via [GitHub Security Advisories](../../security/advisories/new) on this repository
3. Fallback email: security@itcopilot.dev
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Practices

### Secrets Management

- Never commit `.env` files, credentials, or API keys
- Use environment variables for all sensitive configuration
- Rotate `SECRET_KEY` in production deployments
- Use `openssl rand -hex 32` to generate secure keys

### Dependencies

- Dependabot enabled for automated dependency updates
- Bandit security scanning in CI pipeline
- CodeQL analysis for Python vulnerabilities

### Docker

- Production containers run as non-root user
- Multi-stage builds minimize attack surface
- No secrets baked into Docker images

### API Security

- CORS configured via environment variables
- Input validation via Pydantic schemas
- Structured error responses (no stack traces in production)
- File upload size limits enforced

## Security Checklist for Contributors

- [ ] No hardcoded credentials or secrets
- [ ] Input validation on all endpoints
- [ ] Parameterized database queries (SQLAlchemy ORM)
- [ ] Error messages do not leak internal details
- [ ] File uploads validated for type and size
- [ ] Dependencies scanned with Bandit
