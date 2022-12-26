import urllib.request
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from tests.utils.user import create_fake_user


def test_get_me(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `get me` endpoint. """

    request = client.get("/api/users/me", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert "username" in response
    assert "email" in response
    assert "id" in response


def test_get_my_sessions_and_blacklist(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `my session's` endpoint. """

    request = client.get("/api/users/me/sessions", headers=get_user_headers)
    assert request.status_code == 200

    request = client.get("/api/users/me/blocked-users", headers=get_user_headers)
    assert request.status_code == 200


def test_update_me(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `update me` endpoint. """

    data = {"email": "new_email@gmail.com"}

    request = client.put("/api/users/me", json=data, headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert response.get("email") == data["email"]

    data = {"theme": "dark"}

    request = client.put("/api/users/me", json=data, headers=get_user_headers)
    response = request.json()
    assert request.status_code == 200
    assert response.get("settings").get("theme") == data["theme"]


def test_update_my_avatar(client: TestClient, get_user_headers: dict[str, str]) -> None:
    """ Test for `update my avatar` endpoint. """

    file_url = "https://avatars.githubusercontent.com/u/45159366?v=4"
    headers = {'Content-Type': 'multipart/form-data; boundary=--------------------------', **get_user_headers}

    with urllib.request.urlopen(file_url) as response:
        file = response.read()

        request = client.put("/api/users/me/avatar", files={"file": ("avatar.png", file, "image/png")}, headers=headers)
        response = request.json()

        assert request.status_code == 200
        assert "photoURL" in response


def test_add_to_blacklist(client: TestClient, get_user_headers: dict[str, str], db) -> None:
    """ Test for `add to blacklist` endpoint. """

    user = create_fake_user(db)

    data = {"blacklistedUserId": user["id"]}

    # First, we try to block user
    request = client.post("/api/users/blacklist", json=data, headers=get_user_headers)
    assert request.status_code == 200

    # Second, we try to unblock user
    request = client.post("/api/users/blacklist", json=data, headers=get_user_headers)
    assert request.status_code == 200
