# backend/app/auth/routes.py
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import create_access_token, get_current_user, hash_password, verify_password
from app.models import Token, User, UserCreate, UserLogin

router = APIRouter()

# In-memory user store: {username: {"id": str, "email": str, "username": str, "hashed_password": str, "created_at": datetime}}
# This will be replaced with a real database in a future phase.
_users: dict[str, dict] = {}


@router.post(
    "/register",
    response_model=Token,
    status_code=201,
    summary="Register a new user",
    responses={
        201: {"description": "User created, access token returned"},
        409: {"description": "Username or email already registered"},
    },
)
async def register(payload: UserCreate) -> Token:
    """Register a new user account and return a JWT access token.

    - Hashes the password with bcrypt before storage.
    - Rejects duplicate usernames or email addresses with 409.

    Example request::

        POST /api/auth/register
        {"email": "alice@example.com", "username": "alice", "password": "secret"}

    Example response::

        {"access_token": "<jwt>", "token_type": "bearer"}
    """
    if payload.username in _users:
        raise HTTPException(status_code=409, detail="Username already registered")

    if any(u["email"] == payload.email for u in _users.values()):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = str(uuid.uuid4())
    _users[payload.username] = {
        "id": user_id,
        "email": payload.email,
        "username": payload.username,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.utcnow(),
    }

    access_token = create_access_token(data={"sub": user_id})
    return Token(access_token=access_token)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT token",
    responses={
        200: {"description": "Credentials valid, access token returned"},
        401: {"description": "Invalid username or password"},
    },
)
async def login(payload: UserLogin) -> Token:
    """Authenticate an existing user and return a JWT access token.

    Deliberately returns a generic 401 for both unknown username and wrong
    password to avoid leaking account-existence information.

    Example request::

        POST /api/auth/login
        {"username": "alice", "password": "secret"}

    Example response::

        {"access_token": "<jwt>", "token_type": "bearer"}
    """
    user = _users.get(payload.username)
    if user is None or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user["id"]})
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=User,
    summary="Return the currently authenticated user",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Missing or invalid token"},
    },
)
async def me(current_user_id: str = Depends(get_current_user)) -> User:
    """Return profile information for the authenticated user.

    Requires a valid Bearer token in the ``Authorization`` header.

    Example request::

        GET /api/auth/me
        Authorization: Bearer <jwt>

    Example response::

        {"id": "...", "email": "alice@example.com", "username": "alice", "created_at": "..."}
    """
    for user in _users.values():
        if user["id"] == current_user_id:
            return User(
                id=user["id"],
                email=user["email"],
                username=user["username"],
                created_at=user["created_at"],
            )

    raise HTTPException(status_code=404, detail="User not found")
