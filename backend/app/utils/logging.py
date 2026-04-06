# backend/app/utils/logging.py
"""Structured JSON logging configuration for DocuMind.

Call ``setup_logging()`` once at application startup.  After that, all
``logging.getLogger(name)`` calls in the codebase will emit JSON lines to
stdout, which container log aggregators (CloudWatch, Datadog, etc.) can
parse directly.

Log record fields
-----------------
timestamp   ISO-8601 UTC timestamp
level       DEBUG / INFO / WARNING / ERROR / CRITICAL
logger      Logger name (e.g. ``app.rag.routes``)
message     Human-readable message
**extra     Any keyword arguments passed to the logger call
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach any extra fields the caller passed in.
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger to emit JSON to stdout.

    Call this once inside the FastAPI lifespan handler before the app starts
    serving requests.

    Args:
        level: Minimum log level to emit (default ``"INFO"``).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Quiet noisy third-party loggers.
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Convenience wrapper so modules can do::

        from app.utils.logging import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
