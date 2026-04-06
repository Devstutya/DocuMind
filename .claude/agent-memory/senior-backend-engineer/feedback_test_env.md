---
name: Test Environment Setup
description: How to bootstrap the test environment for DocuMind backend without real API keys, and the bcrypt/passlib version constraint
type: feedback
---

Tests must set required env vars before importing `app.main` because `app/config.py` eagerly instantiates `Settings()` at module level, which requires `OPENAI_API_KEY`, `PINECONE_API_KEY`, and `JWT_SECRET_KEY`.

Pattern used in `tests/conftest.py`:
```python
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-openai-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-unit-tests-only")
# then import app.main
```

**bcrypt/passlib constraint:** passlib 1.7.4 has a detection bug with bcrypt >= 4.1. Pin to `bcrypt==4.0.1` in requirements.txt. This must stay pinned until passlib is replaced or updated.

**Why:** bcrypt 5.x was installed; passlib's `_calc_checksum` wrap-bug detection crashes on the newer API. Downgrading to 4.0.1 resolves it.

**How to apply:** Any time requirements.txt is updated, do not bump bcrypt above 4.0.1 without verifying passlib compatibility first.
