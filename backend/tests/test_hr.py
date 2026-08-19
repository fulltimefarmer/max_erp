from httpx import AsyncClient

from tests.test_auth import _login
from tests.test_rbac import _auth, _make_user


async def test_hr_director_can_manage_employees(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "hrboss", role_names=["hr_director"])
    hr_token = await _login(client, "hrboss", "pass12345")

    res = await client.post(
        "/api/v1/hr/departments",
        headers=_auth(hr_token),
        json={"name": "Engineering", "code": "ENG"},
    )
    assert res.status_code == 201
    department_id = res.json()["id"]

    res = await client.post(
        "/api/v1/hr/jobs",
        headers=_auth(hr_token),
        json={"name": "Developer", "code": "DEV", "department_id": department_id},
    )
    assert res.status_code == 201
    job_id = res.json()["id"]

    res = await client.post(
        "/api/v1/hr/employees",
        headers=_auth(hr_token),
        json={
            "name": "John Doe",
            "work_email": "john@example.com",
            "job_id": job_id,
            "department_id": department_id,
        },
    )
    assert res.status_code == 201
    employee = res.json()
    assert employee["name"] == "John Doe"
    assert employee["job_name"] == "Developer"
    assert employee["department_name"] == "Engineering"

    res = await client.get("/api/v1/hr/employees", headers=_auth(hr_token))
    assert res.status_code == 200
    assert any(e["name"] == "John Doe" for e in res.json())

    res = await client.patch(
        f"/api/v1/hr/employees/{employee['id']}",
        headers=_auth(hr_token),
        json={"phone": "555-0100"},
    )
    assert res.status_code == 200
    assert res.json()["phone"] == "555-0100"

    res = await client.delete(f"/api/v1/hr/employees/{employee['id']}", headers=_auth(hr_token))
    assert res.status_code == 204


async def test_normal_user_cannot_access_hr(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "normie")

    user_token = await _login(client, "normie", "pass12345")

    res = await client.get("/api/v1/hr/employees", headers=_auth(user_token))
    assert res.status_code == 403

    res = await client.post(
        "/api/v1/hr/employees",
        headers=_auth(user_token),
        json={"name": "Nope"},
    )
    assert res.status_code == 403


async def test_hr_director_cannot_manage_users(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "hrboss2", role_names=["hr_director"])
    hr_token = await _login(client, "hrboss2", "pass12345")

    res = await client.get("/api/v1/users", headers=_auth(hr_token))
    assert res.status_code == 200

    res = await client.post(
        "/api/v1/users",
        headers=_auth(hr_token),
        json={"username": "intruder", "email": "intruder@example.com", "password": "pass12345"},
    )
    assert res.status_code == 403


async def test_hr_director_permissions(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "hrboss3", role_names=["hr_director"])
    hr_token = await _login(client, "hrboss3", "pass12345")

    res = await client.get("/api/v1/permissions/me", headers=_auth(hr_token))
    assert res.status_code == 200
    body = res.json()

    menu_codes = {m["code"] for m in body["menus"]}
    assert {"hr", "hr.employees", "hr.departments", "hr.jobs"} <= menu_codes
    assert "accounting" not in menu_codes
    assert "settings" not in menu_codes

    access = {a["model"]: a for a in body["model_accesses"]}
    assert access["hr.employee"] == {
        "model": "hr.employee",
        "create": True,
        "read": True,
        "write": True,
        "unlink": True,
    }


async def test_create_employee_with_unknown_job_fails(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "hrboss4", role_names=["hr_director"])
    hr_token = await _login(client, "hrboss4", "pass12345")

    res = await client.post(
        "/api/v1/hr/employees",
        headers=_auth(hr_token),
        json={"name": "Ghost", "job_id": 9999},
    )
    assert res.status_code == 404
