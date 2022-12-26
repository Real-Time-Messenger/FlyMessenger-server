from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from tests.utils.user import create_fake_user


def test_create_dialog(client: TestClient, get_user_headers: dict[str, str], db: AsyncIOMotorClient) -> None:
    """ Test for `create dialog` endpoint. """

    user = create_fake_user(db)

    data = {"toUserId": user["id"]}

    request = client.post("/api/dialogs", json=data, headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response


def test_get_dialogs(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `get dialogs` endpoint. """

    request = client.get("/api/dialogs/me", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response[0]


def test_get_first_dialog_messages(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `get first dialog messages` endpoint. """

    request = client.get("/api/dialogs/me", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response[0]

    dialog_id = response[0]["id"]

    request = client.get(f"/api/dialogs/{dialog_id}/messages", headers=get_user_headers)
    assert request.status_code == 200


def test_update_dialog(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `update dialog` endpoint. """

    request = client.get("/api/dialogs/me", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response[0]

    dialog_id = response[0]["id"]

    data = {"isPinned": True}

    request = client.put(f"/api/dialogs/{dialog_id}", json=data, headers=get_user_headers)
    assert request.status_code == 200

    data = {"isPinned": False}

    request = client.put(f"/api/dialogs/{dialog_id}", json=data, headers=get_user_headers)
    assert request.status_code == 200


def test_delete_dialog(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `delete dialog` endpoint. """

    request = client.get("/api/dialogs/me", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "id" in response[0]

    dialog_id = response[0]["id"]

    request = client.delete(f"/api/dialogs/{dialog_id}", headers=get_user_headers)
    assert request.status_code == 204