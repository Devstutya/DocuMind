# backend/tests/test_utils/test_rate_limit.py
"""Unit tests for the sliding-window rate limiter."""

from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.utils.rate_limit import RateLimiter


def make_limiter(limit: int = 3) -> RateLimiter:
    return RateLimiter(requests_per_minute=limit)


class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        limiter = make_limiter(limit=3)
        limiter.check("user1")
        limiter.check("user1")
        limiter.check("user1")  # exactly at the limit — should not raise

    def test_raises_429_when_limit_exceeded(self):
        limiter = make_limiter(limit=3)
        limiter.check("user1")
        limiter.check("user1")
        limiter.check("user1")
        with pytest.raises(HTTPException) as exc_info:
            limiter.check("user1")
        assert exc_info.value.status_code == 429

    def test_different_users_tracked_independently(self):
        limiter = make_limiter(limit=2)
        limiter.check("alice")
        limiter.check("alice")
        # alice is at limit — bob should still be fine
        limiter.check("bob")
        limiter.check("bob")
        with pytest.raises(HTTPException):
            limiter.check("alice")
        with pytest.raises(HTTPException):
            limiter.check("bob")

    def test_expired_timestamps_are_evicted(self):
        limiter = make_limiter(limit=2)
        # Manually plant old timestamps outside the 60-second window.
        old_time = datetime.now() - timedelta(minutes=2)
        limiter._log["user1"] = [old_time, old_time]

        # The two old entries should be evicted, so this should succeed.
        limiter.check("user1")
        limiter.check("user1")
        # Now we are at the limit with fresh entries.
        with pytest.raises(HTTPException):
            limiter.check("user1")

    def test_error_detail_message(self):
        limiter = make_limiter(limit=1)
        limiter.check("user1")
        with pytest.raises(HTTPException) as exc_info:
            limiter.check("user1")
        assert "Rate limit exceeded" in exc_info.value.detail
