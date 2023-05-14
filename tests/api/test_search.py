from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from tests.utils.user import create_fake_user


def test_global_search(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `global search` endpoint. """

    data = {"query": "test"}
    response = client.get(f"/api/search?query={data['query']}", headers=get_user_headers)
    response_json = response.json()

    assert response.status_code == 200
    assert "dialogs" in response_json
    assert "users" in response_json
    assert "messages" in response_json


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
    request = client.get(f"/api/search/{dialog_id}?query={data['query']}", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "messages" in response