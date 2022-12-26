from fastapi.testclient import TestClient


def test_login(client: TestClient) -> None:
    """ Test for login endpoint. """

    data = {
        "username": "test",
        "password": "123123123"
    }

    request = client.post("/api/test/auth/login", json=data)
    response = request.json()
    assert request.status_code == 200
    assert "token" in response


