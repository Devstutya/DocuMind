# Adding a New API Endpoint

## Project structure
- Routes go in `backend/app/routes/`
- Business logic goes in `backend/app/services/`
- Database models go in `backend/app/models/`
- Schemas/validation go in `backend/app/schemas/`

## Steps to add an endpoint
1. Define the Pydantic schema in `schemas/`
2. Write the service function in `services/`
3. Create the route in `routes/` using FastAPI's APIRouter
4. Register the router in `main.py`
5. Add tests in `tests/`

## Conventions
- All routes are prefixed with `/api/v1/`
- Use dependency injection for DB sessions
- JWT auth is required on all routes except `/auth/login` and `/auth/register`
- Return consistent response format: `{"status": "success", "data": {...}}`