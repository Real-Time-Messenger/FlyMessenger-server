from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from tests.utils.user import create_fake_user


def test_global_search(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `global search` endpoint. """

    data = {"query": "test"}
    request = client.get(f"/api/search/{data['query']}", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "dialogs" in response
    assert "users" in response
    assert "messages" in response


def test_in_dialog_search(client: TestClient, get_user_headers: dict[str, str], db: AsyncIOMotorClient) -> None:
    """ Test for `in dialog search` endpoint. """

    user = create_fake_user(db)

    data = {"toUserId": user["id"]}

    request = client.post("/api/dialogs", json=data, headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response

    dialog_id = response["id"]

    data = {"query": "test"}
    request = client.get(f"/api/search/{dialog_id}/{data['query']}", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "messages" in response