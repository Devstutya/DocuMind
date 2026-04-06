# backend/app/utils/rate_limit.py
"""Sliding-window rate limiter for per-user API requests.

Limits each user to ``RATE_LIMIT_PER_MINUTE`` requests within any rolling
60-second window.  Raises HTTP 429 when the limit is exceeded.
"""

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException

from app.auth.jwt import get_current_user
from app.config import settings


class RateLimiter:
    """In-process sliding-window rate limiter keyed by user ID."""

    def __init__(self, requests_per_minute: int = 20) -> None:
        self.requests_per_minute = requests_per_minute
        self._log: dict[str, list[datetime]] = defaultdict(list)

    def check(self, user_id: str) -> None:
        """Record a request for *user_id* and raise 429 if the limit is hit.

        Args:
            user_id: Unique identifier for the user (JWT ``sub`` claim).

        Raises:
            HTTPException: 429 if the user has exceeded the rate limit.
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=1)

        # Discard timestamps outside the current window.
        self._log[user_id] = [t for t in self._log[user_id] if t > window_start]

        if len(self._log[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please wait a moment before retrying.",
            )

        self._log[user_id].append(now)


# Singleton — shared across all requests in the process.
rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


async def require_rate_limit(
    current_user_id: str = Depends(get_current_user),
) -> str:
    """FastAPI dependency that enforces rate limiting for authenticated routes.

    Intended to be added to router dependencies or individual endpoints via
    ``Depends(require_rate_limit)``.

    Returns:
        The authenticated user ID (so callers can reuse it without a second
        ``Depends(get_current_user)`` call).
    """
    rate_limiter.check(current_user_id)
    return current_user_id
