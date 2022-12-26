from typing import Generator

import pytest
from starlette.testclient import TestClient

from app.database.main import get_database
from app.main import app
from tests.utils.user import user_authentication_headers


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def db() -> Generator:
    return get_database()


@pytest.fixture(scope="module")
def get_user_headers(client: TestClient) -> dict[str, str]:
    return user_authentication_headers(
        client=client
    )
