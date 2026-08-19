from httpx import AsyncClient

from tests.test_auth import _login


async def test_list_users_as_root(client: AsyncClient):
    token = await _login(client)
    res = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    users = res.json()
    assert any(u["username"] == "root" for u in users)


async def test_create_user_as_root(client: AsyncClient):
    token = await _login(client)
    res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "alice", "email": "alice@example.com", "password": "alicepass123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "alice"
    assert any(role["name"] == "user" for role in body["roles"])


async def test_create_duplicate_user(client: AsyncClient):
    token = await _login(client)
    res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "root", "email": "root2@example.com", "password": "rootpass123"},
    )
    assert res.status_code == 409


async def test_new_user_can_login(client: AsyncClient):
    token = await _login(client)
    await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "bob", "email": "bob@example.com", "password": "bobpass123"},
    )

    res = await client.post("/api/v1/auth/login", data={"username": "bob", "password": "bobpass123"})
    assert res.status_code == 200
