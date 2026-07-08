# Contributing

Thank you for your interest in contributing to ITcopilot! Please read this guide before submitting contributions.

## Code of Conduct

All contributors must follow our [Code of Conduct](../CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes
6. Run tests: `pytest`
7. Run linting: `ruff check . && mypy apps/api/app packages`
8. Commit with a descriptive message
9. Push and open a Pull Request

## Development Standards

- **Type hints**: All Python code must be fully typed
- **Docstrings**: Google-style docstrings for public APIs
- **Tests**: New features require corresponding tests
- **Logging**: Use loguru for all logging
- **Error handling**: Use custom exceptions from `app.core.exceptions`
- **No placeholders**: No TODO comments, pass statements, or fake implementations

## Commit Messages

Follow conventional commit format:

```
type(scope): description

feat(tax): add new regime slab rates for AY 2026-27
fix(api): handle empty PAN in assessment listing
docs(readme): update Docker setup instructions
test(engine): add surcharge calculation tests
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`

## Pull Request Process

1. Ensure CI passes (lint, type check, tests, security scan)
2. Update documentation if needed
3. Add CHANGELOG entry under `[Unreleased]`
4. Request review from maintainers
5. Address review feedback
6. Squash commits if requested

## Reporting Issues

Use GitHub Issues with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)

## Security Issues

Do NOT open public issues for security vulnerabilities. See [SECURITY.md](../SECURITY.md).
