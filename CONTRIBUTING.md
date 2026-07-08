# Contributing to ITcopilot

Thank you for your interest in contributing! Please read the full [Contributing Guide](docs/contributing.md) for detailed instructions.

## Quick Start

```bash
git clone https://github.com/nbhushan108/ITcopilot.git
cd itcopilot
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pytest
```

## Pull Requests

1. Fork the repo and create a feature branch
2. Write tests for new functionality
3. Ensure all CI checks pass (ruff, mypy, pytest >= 95% coverage)
4. Submit a PR using the pull request template

## Code Standards

- Fully typed Python with strict MyPy
- Google-style docstrings
- Ruff for linting and formatting
- No hardcoded secrets or credentials

See [docs/contributing.md](docs/contributing.md) for the complete guide.
