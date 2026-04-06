# Database Conventions

- Using PostgreSQL with SQLAlchemy ORM
- Migrations managed with Alembic
- All models inherit from `Base` in `app/database.py`
- Every table has: `id` (UUID), `created_at`, `updated_at`
- To create a migration: `alembic revision --autogenerate -m "description"`
- To apply: `alembic upgrade head`
- Foreign keys use `ondelete="CASCADE"` unless specified otherwise