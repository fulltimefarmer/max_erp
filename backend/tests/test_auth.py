from httpx import AsyncClient


async def _login(client: AsyncClient, username: str = "root", password: str = "rootpass") -> str:
    res = await client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


async def test_health(client: AsyncClient):
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_login_success(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", data={"username": "root", "password": "rootpass"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


async def test_login_wrong_password(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", data={"username": "root", "password": "wrong"})
    assert res.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", data={"username": "nobody", "password": "whatever"})
    assert res.status_code == 401


async def test_me(client: AsyncClient):
    token = await _login(client)
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "root"


async def test_me_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


async def test_refresh_flow(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", data={"username": "root", "password": "rootpass"})
    refresh_token = res.json()["refresh_token"]

    refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


async def test_users_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/users")
    assert res.status_code == 401
