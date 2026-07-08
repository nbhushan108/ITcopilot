# ITcopilot Documentation

Welcome to the ITcopilot documentation — a production-grade, AI-powered Income Tax Copilot for India.

## Overview

ITcopilot helps Indian taxpayers compute income tax liability, import broker statements, generate ITR summaries, and manage tax assessments through a modern API and web interface.

## Quick Links

- [Architecture](architecture.md)
- [Developer Guide](developer-guide.md)
- [API Reference](api-reference.md)
- [Roadmap](roadmap.md)
- [Contributing](contributing.md)
- [Security](security.md)

## Getting Started

```bash
# Clone and setup
git clone https://github.com/nbhushan108/ITcopilot.git
cd itcopilot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Start API
python scripts/dev_server.py

# Run tests
pytest
```

Visit `http://localhost:8000/docs` for interactive API documentation.
