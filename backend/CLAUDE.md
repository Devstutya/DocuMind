# Backend Agent Rules

You are working on the DocuMind backend — a FastAPI + PostgreSQL
application for PDF document intelligence.

## Your role
- You only modify files inside `backend/`
- Never touch frontend code
- Follow REST conventions strictly
- Every endpoint needs: validation, error handling, tests

## Stack
- Python 3.11, FastAPI, SQLAlchemy, Alembic
- PostgreSQL with pgvector for embeddings
- PyMuPDF for PDF extraction
- OpenAI API for embeddings

## Before making changes
1. Read the relevant skill in `.claude/skills/`
2. Check existing patterns in the codebase
3. Run tests after every change: `pytest backend/tests/`

## Testing Rules
- Every new endpoint, service function, or model gets tests
- Tests live in `backend/tests/` mirroring the source structure:
  - `tests/test_routes/` for API endpoint tests
  - `tests/test_services/` for business logic tests
  - `tests/test_models/` for model/schema tests
- Use pytest + httpx AsyncClient for endpoint tests
- Use a test database, never the dev database
- Fixtures go in `conftest.py`
- Test the happy path, validation errors, auth failures,
  and edge cases (empty input, duplicates, not found)
- Run tests after every change: `pytest backend/tests/ -v`
- Aim for: if a test file doesn't exist for a module you're
  touching, create it before writing the feature