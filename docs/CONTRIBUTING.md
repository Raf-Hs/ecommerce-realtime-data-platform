# Contributing

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Development setup

1. Clone the repository.
2. Create a Python virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy env template: `cp .env.example .env` and edit values.
5. Start infrastructure: `docker compose up -d` (Phase 1+).

## Conventions

- All code, docs, identifiers, and commit messages in English.
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Type hints where appropriate; structured logging; env-based config.
- Tests required for non-trivial logic.
- No secrets or datasets committed.

## Branching

Feature branches off `main`; PRs reviewed before merge. (Single-developer
workflow acceptable for portfolio.)