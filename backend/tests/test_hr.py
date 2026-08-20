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


async def _setup_hr(client: AsyncClient, username: str = "hrboss") -> str:
    root_token = await _login(client)
    await _make_user(client, root_token, username, role_names=["hr_director"])
    return await _login(client, username, "pass12345")


async def _create_employee(client: AsyncClient, hr_token: str, name: str = "Jane Doe") -> int:
    res = await client.post("/api/v1/hr/employees", headers=_auth(hr_token), json={"name": name})
    assert res.status_code == 201
    return res.json()["id"]


async def _first_leave_type_id(client: AsyncClient, hr_token: str) -> int:
    res = await client.get("/api/v1/hr/leave-types", headers=_auth(hr_token))
    assert res.status_code == 200
    types = res.json()
    assert types, "leave types should be seeded"
    return types[0]["id"]


async def test_leave_request_approve_flow(client: AsyncClient):
    hr_token = await _setup_hr(client, "hrboss5")
    employee_id = await _create_employee(client, hr_token)
    leave_type_id = await _first_leave_type_id(client, hr_token)

    res = await client.post(
        "/api/v1/hr/leaves",
        headers=_auth(hr_token),
        json={
            "employee_id": employee_id,
            "leave_type_id": leave_type_id,
            "date_from": "2026-09-01",
            "date_to": "2026-09-03",
            "description": "Summer break",
        },
    )
    assert res.status_code == 201
    leave = res.json()
    assert leave["state"] == "draft"
    assert leave["number_of_days"] == 3
    assert leave["employee_name"] == "Jane Doe"

    res = await client.post(f"/api/v1/hr/leaves/{leave['id']}/approve", headers=_auth(hr_token))
    assert res.status_code == 200
    approved = res.json()
    assert approved["state"] == "approved"
    assert approved["approved_by"] == "hrboss5"
    assert approved["approved_at"] is not None


async def test_leave_request_refuse_flow(client: AsyncClient):
    hr_token = await _setup_hr(client, "hrboss6")
    employee_id = await _create_employee(client, hr_token)
    leave_type_id = await _first_leave_type_id(client, hr_token)

    res = await client.post(
        "/api/v1/hr/leaves",
        headers=_auth(hr_token),
        json={
            "employee_id": employee_id,
            "leave_type_id": leave_type_id,
            "date_from": "2026-10-01",
            "date_to": "2026-10-01",
        },
    )
    assert res.status_code == 201
    leave_id = res.json()["id"]

    res = await client.post(f"/api/v1/hr/leaves/{leave_id}/refuse", headers=_auth(hr_token))
    assert res.status_code == 200
    assert res.json()["state"] == "refused"

    res = await client.post(f"/api/v1/hr/leaves/{leave_id}/approve", headers=_auth(hr_token))
    assert res.status_code == 400


async def test_leave_date_validation(client: AsyncClient):
    hr_token = await _setup_hr(client, "hrboss7")
    employee_id = await _create_employee(client, hr_token)
    leave_type_id = await _first_leave_type_id(client, hr_token)

    res = await client.post(
        "/api/v1/hr/leaves",
        headers=_auth(hr_token),
        json={
            "employee_id": employee_id,
            "leave_type_id": leave_type_id,
            "date_from": "2026-11-10",
            "date_to": "2026-11-05",
        },
    )
    assert res.status_code == 400


async def test_appraisal_complete_flow(client: AsyncClient):
    hr_token = await _setup_hr(client, "hrboss8")
    employee_id = await _create_employee(client, hr_token)

    res = await client.post(
        "/api/v1/hr/appraisals",
        headers=_auth(hr_token),
        json={"employee_id": employee_id, "appraisal_date": "2026-12-15", "goals": "Grow the team"},
    )
    assert res.status_code == 201
    appraisal = res.json()
    assert appraisal["state"] == "draft"

    res = await client.post(f"/api/v1/hr/appraisals/{appraisal['id']}/complete", headers=_auth(hr_token))
    assert res.status_code == 400

    res = await client.patch(
        f"/api/v1/hr/appraisals/{appraisal['id']}",
        headers=_auth(hr_token),
        json={"final_rating": 5, "feedback": "Great work"},
    )
    assert res.status_code == 200
    assert res.json()["final_rating"] == 5

    res = await client.post(f"/api/v1/hr/appraisals/{appraisal['id']}/complete", headers=_auth(hr_token))
    assert res.status_code == 200
    assert res.json()["state"] == "done"


async def test_normal_user_cannot_access_leaves(client: AsyncClient):
    root_token = await _login(client)
    await _make_user(client, root_token, "normie2")

    user_token = await _login(client, "normie2", "pass12345")
    res = await client.get("/api/v1/hr/leaves", headers=_auth(user_token))
    assert res.status_code == 403
    res = await client.get("/api/v1/hr/appraisals", headers=_auth(user_token))
    assert res.status_code == 403
