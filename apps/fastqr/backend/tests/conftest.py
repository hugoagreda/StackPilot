from collections.abc import Generator
import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Must be set before importing app modules that read env vars at import time.
os.environ.setdefault("FASTQR_JWT_SECRET", "test-secret-not-for-production")

from app.db import get_db
from app.main import app


def _fake_get_db() -> Generator[None, None, None]:
    yield None


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = _fake_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
