from httpx import AsyncClient

from tests.test_auth import _login


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _make_user(
    client: AsyncClient, token: str, username: str, role_names: list[str] | None = None
) -> int:
    res = await client.post(
        "/api/v1/users",
        headers=_auth(token),
        json={"username": username, "email": f"{username}@example.com", "password": "pass12345"},
    )
    assert res.status_code == 201
    user_id = res.json()["id"]

    if role_names:
        res = await client.patch(
            f"/api/v1/users/{user_id}",
            headers=_auth(token),
            json={"role_names": role_names},
        )
        assert res.status_code == 200
    return user_id


async def test_user_role_has_read_only_model_access(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "alice")

    alice_token = await _login(client, "alice", "pass12345")

    res = await client.get("/api/v1/users", headers=_auth(alice_token))
    assert res.status_code == 200

    res = await client.post(
        "/api/v1/users",
        headers=_auth(alice_token),
        json={"username": "carol", "email": "carol@example.com", "password": "pass12345"},
    )
    assert res.status_code == 403

    res = await client.delete("/api/v1/users/1", headers=_auth(alice_token))
    assert res.status_code == 403


async def test_manager_cannot_unlink_users(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "manager1", role_names=["manager"])

    manager_token = await _login(client, "manager1", "pass12345")

    res = await client.get("/api/v1/users", headers=_auth(manager_token))
    assert res.status_code == 200

    res = await client.post(
        "/api/v1/users",
        headers=_auth(manager_token),
        json={"username": "bob", "email": "bob@example.com", "password": "pass12345"},
    )
    assert res.status_code == 201
    bob_id = res.json()["id"]

    res = await client.delete(f"/api/v1/users/{bob_id}", headers=_auth(manager_token))
    assert res.status_code == 403


async def test_user_cannot_access_admin_config(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "alice2")

    alice_token = await _login(client, "alice2", "pass12345")

    res = await client.get("/api/v1/menus", headers=_auth(alice_token))
    assert res.status_code == 403

    res = await client.post(
        "/api/v1/menus",
        headers=_auth(alice_token),
        json={"name": "Reports", "code": "reports"},
    )
    assert res.status_code == 403


async def test_manager_can_manage_menus_but_not_model_access(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "manager2", role_names=["manager"])

    manager_token = await _login(client, "manager2", "pass12345")

    res = await client.get("/api/v1/menus", headers=_auth(manager_token))
    assert res.status_code == 200

    res = await client.post(
        "/api/v1/menus",
        headers=_auth(manager_token),
        json={"name": "Reports", "code": "reports"},
    )
    assert res.status_code == 201

    res = await client.get("/api/v1/model-accesses", headers=_auth(manager_token))
    assert res.status_code == 200

    res = await client.put(
        "/api/v1/model-accesses",
        headers=_auth(manager_token),
        json={"model": "res.users", "role_name": "user", "perm_read": True},
    )
    assert res.status_code == 403


async def test_permissions_me_root(client: AsyncClient):
    token = await _login(client)
    res = await client.get("/api/v1/permissions/me", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()

    menu_codes = {m["code"] for m in body["menus"]}
    page_codes = {p["code"] for p in body["pages"]}
    assert {"dashboard", "sales", "accounting", "settings"} <= menu_codes
    assert {"dashboard", "accounting", "settings.access"} <= page_codes

    access = {a["model"]: a for a in body["model_accesses"]}
    assert access["res.users"] == {"model": "res.users", "create": True, "read": True, "write": True, "unlink": True}


async def test_permissions_me_user(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "alice3")

    alice_token = await _login(client, "alice3", "pass12345")
    res = await client.get("/api/v1/permissions/me", headers=_auth(alice_token))
    assert res.status_code == 200
    body = res.json()

    menu_codes = {m["code"] for m in body["menus"]}
    page_codes = {p["code"] for p in body["pages"]}
    assert menu_codes == {"dashboard", "profile"}
    assert page_codes == {"dashboard", "profile"}

    access = {a["model"]: a for a in body["model_accesses"]}
    assert access["res.users"]["read"] is True
    assert access["res.users"]["write"] is False


async def test_permissions_me_manager(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "manager3", role_names=["manager"])

    manager_token = await _login(client, "manager3", "pass12345")
    res = await client.get("/api/v1/permissions/me", headers=_auth(manager_token))
    assert res.status_code == 200
    body = res.json()

    menu_codes = {m["code"] for m in body["menus"]}
    assert {"dashboard", "sales", "sales.orders", "inventory", "inventory.products"} <= menu_codes
    assert "accounting" not in menu_codes
    assert "settings" not in menu_codes


async def test_grant_model_access_then_user_can_create(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "alice4")

    res = await client.put(
        "/api/v1/model-accesses",
        headers=_auth(token),
        json={
            "model": "res.users",
            "role_name": "user",
            "perm_create": True,
            "perm_read": True,
            "perm_write": False,
            "perm_unlink": False,
        },
    )
    assert res.status_code == 200

    alice_token = await _login(client, "alice4", "pass12345")
    res = await client.post(
        "/api/v1/users",
        headers=_auth(alice_token),
        json={"username": "dave", "email": "dave@example.com", "password": "pass12345"},
    )
    assert res.status_code == 201


async def test_set_menu_roles_grants_visibility(client: AsyncClient):
    token = await _login(client)
    await _make_user(client, token, "alice5")

    res = await client.get("/api/v1/menus", headers=_auth(token))
    assert res.status_code == 200
    accounting = next(m for m in res.json() if m["code"] == "accounting")

    res = await client.put(
        f"/api/v1/menus/{accounting['id']}/roles",
        headers=_auth(token),
        json={"role_names": ["root", "user"]},
    )
    assert res.status_code == 200

    alice_token = await _login(client, "alice5", "pass12345")
    res = await client.get("/api/v1/permissions/me", headers=_auth(alice_token))
    menu_codes = {m["code"] for m in res.json()["menus"]}
    assert "accounting" in menu_codes
