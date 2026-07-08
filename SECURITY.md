# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities through **GitHub Security Advisories** on this repository (Security → Advisories → Report a vulnerability). Do not open public issues for security concerns.

For repositories without GitHub advisory access, email **security@itcopilot.dev** as a fallback.

See our full [Security Policy](docs/security.md) for details on supported versions, reporting process, and security practices.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Security Practices

- No secrets in source code or Docker images
- Bandit and CodeQL scanning in CI
- Input validation on all API endpoints
- Production containers run as non-root user
