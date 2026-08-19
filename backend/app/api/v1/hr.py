from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_model_access
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.hr import Department, Employee, JobPosition
from app.models.user import User
from app.schemas.hr import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
    JobPositionCreate,
    JobPositionRead,
    JobPositionUpdate,
)

router = APIRouter(tags=["hr"])
logger = get_logger(__name__)

require_employee_read = require_model_access("hr.employee", "read")
require_employee_create = require_model_access("hr.employee", "create")
require_employee_write = require_model_access("hr.employee", "write")
require_employee_unlink = require_model_access("hr.employee", "unlink")

require_department_read = require_model_access("hr.department", "read")
require_department_create = require_model_access("hr.department", "create")
require_department_write = require_model_access("hr.department", "write")
require_department_unlink = require_model_access("hr.department", "unlink")

require_job_read = require_model_access("hr.job", "read")
require_job_create = require_model_access("hr.job", "create")
require_job_write = require_model_access("hr.job", "write")
require_job_unlink = require_model_access("hr.job", "unlink")


async def _get_or_404(db: AsyncSession, model, obj_id: int | None, label: str):
    if obj_id is None:
        return None
    obj = (await db.execute(select(model).where(model.id == obj_id))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found")
    return obj


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
departments_router = APIRouter(prefix="/hr/departments")


@departments_router.get("", response_model=list[DepartmentRead])
async def list_departments(
    _: Annotated[User, Depends(require_department_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Department]:
    result = await db.execute(select(Department).order_by(Department.id))
    return list(result.scalars().all())


@departments_router.post("", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    _: Annotated[User, Depends(require_department_create)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Department:
    await _get_or_404(db, Department, payload.parent_id, "Parent department")

    department = Department(**payload.model_dump())
    db.add(department)
    await db.commit()
    department = (
        await db.execute(select(Department).where(Department.id == department.id))
    ).scalar_one()
    logger.info("department_created", name=department.name)
    return department


@departments_router.get("/{department_id}", response_model=DepartmentRead)
async def get_department(
    department_id: int,
    _: Annotated[User, Depends(require_department_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Department:
    department = (
        await db.execute(select(Department).where(Department.id == department_id))
    ).scalar_one_or_none()
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department


@departments_router.patch("/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    _: Annotated[User, Depends(require_department_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Department:
    department = (
        await db.execute(select(Department).where(Department.id == department_id))
    ).scalar_one_or_none()
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "parent_id" and value is not None and value != department_id:
            await _get_or_404(db, Department, value, "Parent department")
        setattr(department, field, value)

    await db.commit()
    department = (
        await db.execute(select(Department).where(Department.id == department.id))
    ).scalar_one()
    logger.info("department_updated", name=department.name)
    return department


@departments_router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    _: Annotated[User, Depends(require_department_unlink)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    department = (
        await db.execute(select(Department).where(Department.id == department_id))
    ).scalar_one_or_none()
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    await db.delete(department)
    await db.commit()
    logger.info("department_deleted", id=department_id)


# ---------------------------------------------------------------------------
# Job positions
# ---------------------------------------------------------------------------
jobs_router = APIRouter(prefix="/hr/jobs")


@jobs_router.get("", response_model=list[JobPositionRead])
async def list_jobs(
    _: Annotated[User, Depends(require_job_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[JobPosition]:
    result = await db.execute(select(JobPosition).order_by(JobPosition.id))
    return list(result.scalars().all())


@jobs_router.post("", response_model=JobPositionRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobPositionCreate,
    _: Annotated[User, Depends(require_job_create)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobPosition:
    await _get_or_404(db, Department, payload.department_id, "Department")

    job = JobPosition(**payload.model_dump())
    db.add(job)
    await db.commit()
    job = (await db.execute(select(JobPosition).where(JobPosition.id == job.id))).scalar_one()
    logger.info("job_created", name=job.name)
    return job


@jobs_router.get("/{job_id}", response_model=JobPositionRead)
async def get_job(
    job_id: int,
    _: Annotated[User, Depends(require_job_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobPosition:
    job = (await db.execute(select(JobPosition).where(JobPosition.id == job_id))).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job position not found")
    return job


@jobs_router.patch("/{job_id}", response_model=JobPositionRead)
async def update_job(
    job_id: int,
    payload: JobPositionUpdate,
    _: Annotated[User, Depends(require_job_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobPosition:
    job = (await db.execute(select(JobPosition).where(JobPosition.id == job_id))).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job position not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "department_id" and value is not None:
            await _get_or_404(db, Department, value, "Department")
        setattr(job, field, value)

    await db.commit()
    job = (await db.execute(select(JobPosition).where(JobPosition.id == job.id))).scalar_one()
    logger.info("job_updated", name=job.name)
    return job


@jobs_router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    _: Annotated[User, Depends(require_job_unlink)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    job = (await db.execute(select(JobPosition).where(JobPosition.id == job_id))).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job position not found")

    await db.delete(job)
    await db.commit()
    logger.info("job_deleted", id=job_id)


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------
employees_router = APIRouter(prefix="/hr/employees")


@employees_router.get("", response_model=list[EmployeeRead])
async def list_employees(
    _: Annotated[User, Depends(require_employee_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Employee]:
    result = await db.execute(select(Employee).order_by(Employee.id))
    return list(result.scalars().all())


@employees_router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    _: Annotated[User, Depends(require_employee_create)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Employee:
    await _get_or_404(db, JobPosition, payload.job_id, "Job position")
    await _get_or_404(db, Department, payload.department_id, "Department")
    await _get_or_404(db, Employee, payload.manager_id, "Manager")
    await _get_or_404(db, User, payload.user_id, "User")

    employee = Employee(**payload.model_dump())
    db.add(employee)
    await db.commit()
    employee = (await db.execute(select(Employee).where(Employee.id == employee.id))).scalar_one()
    logger.info("employee_created", name=employee.name)
    return employee


@employees_router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(
    employee_id: int,
    _: Annotated[User, Depends(require_employee_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Employee:
    employee = (
        await db.execute(select(Employee).where(Employee.id == employee_id))
    ).scalar_one_or_none()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@employees_router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    _: Annotated[User, Depends(require_employee_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Employee:
    employee = (
        await db.execute(select(Employee).where(Employee.id == employee_id))
    ).scalar_one_or_none()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "job_id":
            await _get_or_404(db, JobPosition, value, "Job position")
        elif field == "department_id":
            await _get_or_404(db, Department, value, "Department")
        elif field == "manager_id":
            if value == employee_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot be its own manager")
            await _get_or_404(db, Employee, value, "Manager")
        elif field == "user_id":
            await _get_or_404(db, User, value, "User")
        setattr(employee, field, value)

    await db.commit()
    employee = (await db.execute(select(Employee).where(Employee.id == employee.id))).scalar_one()
    logger.info("employee_updated", name=employee.name)
    return employee


@employees_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    _: Annotated[User, Depends(require_employee_unlink)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    employee = (
        await db.execute(select(Employee).where(Employee.id == employee_id))
    ).scalar_one_or_none()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    await db.delete(employee)
    await db.commit()
    logger.info("employee_deleted", id=employee_id)


router.include_router(departments_router)
router.include_router(jobs_router)
router.include_router(employees_router)
