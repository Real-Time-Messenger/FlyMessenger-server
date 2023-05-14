import base64
import urllib

from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from tests.utils.user import create_fake_user


def test_websocket_send_message(client: TestClient, get_user_headers: dict[str, str], db: AsyncIOMotorClient) -> None:
    """ Test for websocket send message. """

    token = get_user_headers["Authorization"].split(" ")[1]

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        user = create_fake_user(db)

        data = {"toUserId": user["id"]}

        request = client.post("/api/dialogs", json=data, headers=get_user_headers)
        response = request.json()
        assert request.status_code == 200
        assert "id" in response

        dialog_id = response["id"]

        websocket.send_json({"dialogId": dialog_id, "text": "test", "file": None, "type": "SEND_MESSAGE", "recipientId": user["id"]})

        data = websocket.receive_json()
        assert data["type"] == "RECEIVE_MESSAGE"
        assert data["dialog"]["id"] == dialog_id
        assert data["message"]["text"] == "test"

    request = client.get(f"/api/dialogs/{dialog_id}/messages", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert response[0]["text"] == "test"


def test_websocket_send_message_with_file(client: TestClient, get_user_headers: dict[str, str], db: AsyncIOMotorClient) -> None:
    """ Test for websocket send message with file. """

    token = get_user_headers["Authorization"].split(" ")[1]

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        user = create_fake_user(db)

        data = {"toUserId": user["id"]}

        request = client.post("/api/dialogs", json=data, headers=get_user_headers)
        response = request.json()
        assert request.status_code == 200
        assert "id" in response

        dialog_id = response["id"]

        file_url = "https://avatars.githubusercontent.com/u/45159366?v=4"
        with urllib.request.urlopen(file_url) as file:
            file = file.read()
            file_data = {
                "name": "test.png",
                "type": "image/png",
                "size": len(file),
                "data": base64.b64encode(file).decode("utf-8"),
            }

            websocket.send_json({"dialogId": dialog_id, "text": "test", "file": file_data, "type": "SEND_MESSAGE", "recipientId": user["id"]})

        data = websocket.receive_json()

        print(data)

        assert data["type"] == "RECEIVE_MESSAGE"
        assert data["dialog"]["id"] == dialog_id

    request = client.get(f"/api/dialogs/{dialog_id}/messages", headers=get_user_headers)
    response = request.json()

    assert request.status_code == 200
    assert response[-1]["text"] == "test"