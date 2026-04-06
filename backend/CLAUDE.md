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