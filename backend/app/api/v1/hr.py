from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_model_access
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.hr import Appraisal, Department, Employee, JobPosition, LeaveRequest, LeaveType
from app.models.user import User
from app.schemas.hr import (
    AppraisalCreate,
    AppraisalRead,
    AppraisalUpdate,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
    JobPositionCreate,
    JobPositionRead,
    JobPositionUpdate,
    LeaveRequestCreate,
    LeaveRequestRead,
    LeaveRequestUpdate,
    LeaveTypeCreate,
    LeaveTypeRead,
)

router = APIRouter(tags=["hr"])
logger = get_logger(__name__)

LEAVE_DRAFT = "draft"
LEAVE_APPROVED = "approved"
LEAVE_REFUSED = "refused"
APPRAISAL_DRAFT = "draft"
APPRAISAL_DONE = "done"

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

require_leave_type_read = require_model_access("hr.leave.type", "read")
require_leave_type_write = require_model_access("hr.leave.type", "write")

require_leave_read = require_model_access("hr.leave", "read")
require_leave_create = require_model_access("hr.leave", "create")
require_leave_write = require_model_access("hr.leave", "write")
require_leave_unlink = require_model_access("hr.leave", "unlink")

require_appraisal_read = require_model_access("hr.appraisal", "read")
require_appraisal_create = require_model_access("hr.appraisal", "create")
require_appraisal_write = require_model_access("hr.appraisal", "write")
require_appraisal_unlink = require_model_access("hr.appraisal", "unlink")


def _compute_days(date_from, date_to) -> int:
    if date_to < date_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_to must be on or after date_from",
        )
    return (date_to - date_from).days + 1


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


# ---------------------------------------------------------------------------
# Leave types
# ---------------------------------------------------------------------------
leave_types_router = APIRouter(prefix="/hr/leave-types")


@leave_types_router.get("", response_model=list[LeaveTypeRead])
async def list_leave_types(
    _: Annotated[User, Depends(require_leave_type_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LeaveType]:
    result = await db.execute(select(LeaveType).order_by(LeaveType.id))
    return list(result.scalars().all())


@leave_types_router.post("", response_model=LeaveTypeRead, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    payload: LeaveTypeCreate,
    _: Annotated[User, Depends(require_leave_type_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveType:
    existing = (
        await db.execute(select(LeaveType).where(LeaveType.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Leave type code already exists")

    leave_type = LeaveType(**payload.model_dump())
    db.add(leave_type)
    await db.commit()
    leave_type = (
        await db.execute(select(LeaveType).where(LeaveType.id == leave_type.id))
    ).scalar_one()
    logger.info("leave_type_created", code=leave_type.code)
    return leave_type


# ---------------------------------------------------------------------------
# Leave requests
# ---------------------------------------------------------------------------
leaves_router = APIRouter(prefix="/hr/leaves")


@leaves_router.get("", response_model=list[LeaveRequestRead])
async def list_leaves(
    _: Annotated[User, Depends(require_leave_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LeaveRequest]:
    result = await db.execute(
        select(LeaveRequest).order_by(LeaveRequest.date_from.desc(), LeaveRequest.id)
    )
    return list(result.scalars().all())


@leaves_router.post("", response_model=LeaveRequestRead, status_code=status.HTTP_201_CREATED)
async def create_leave(
    payload: LeaveRequestCreate,
    _: Annotated[User, Depends(require_leave_create)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveRequest:
    await _get_or_404(db, Employee, payload.employee_id, "Employee")
    await _get_or_404(db, LeaveType, payload.leave_type_id, "Leave type")

    leave = LeaveRequest(
        **payload.model_dump(),
        number_of_days=_compute_days(payload.date_from, payload.date_to),
        state=LEAVE_DRAFT,
    )
    db.add(leave)
    await db.commit()
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave.id))).scalar_one()
    logger.info("leave_created", employee_id=leave.employee_id)
    return leave


@leaves_router.get("/{leave_id}", response_model=LeaveRequestRead)
async def get_leave(
    leave_id: int,
    _: Annotated[User, Depends(require_leave_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveRequest:
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))).scalar_one_or_none()
    if leave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    return leave


@leaves_router.patch("/{leave_id}", response_model=LeaveRequestRead)
async def update_leave(
    leave_id: int,
    payload: LeaveRequestUpdate,
    _: Annotated[User, Depends(require_leave_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveRequest:
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))).scalar_one_or_none()
    if leave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    if leave.state != LEAVE_DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft leave requests can be edited")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "employee_id":
            if value is None:
                continue
            await _get_or_404(db, Employee, value, "Employee")
        elif field == "leave_type_id":
            if value is None:
                continue
            await _get_or_404(db, LeaveType, value, "Leave type")
        elif field in ("date_from", "date_to") and value is None:
            continue
        setattr(leave, field, value)

    leave.number_of_days = _compute_days(leave.date_from, leave.date_to)

    await db.commit()
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave.id))).scalar_one()
    logger.info("leave_updated", id=leave.id)
    return leave


@leaves_router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_leave(
    leave_id: int,
    _: Annotated[User, Depends(require_leave_unlink)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))).scalar_one_or_none()
    if leave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    await db.delete(leave)
    await db.commit()
    logger.info("leave_deleted", id=leave_id)


@leaves_router.post("/{leave_id}/approve", response_model=LeaveRequestRead)
async def approve_leave(
    leave_id: int,
    current_user: Annotated[User, Depends(require_leave_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveRequest:
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))).scalar_one_or_none()
    if leave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    if leave.state != LEAVE_DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft leave requests can be approved")

    leave.state = LEAVE_APPROVED
    leave.approved_by = current_user.username
    leave.approved_at = datetime.now(UTC)

    await db.commit()
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave.id))).scalar_one()
    logger.info("leave_approved", id=leave.id, by=current_user.username)
    return leave


@leaves_router.post("/{leave_id}/refuse", response_model=LeaveRequestRead)
async def refuse_leave(
    leave_id: int,
    current_user: Annotated[User, Depends(require_leave_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeaveRequest:
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))).scalar_one_or_none()
    if leave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    if leave.state != LEAVE_DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft leave requests can be refused")

    leave.state = LEAVE_REFUSED

    await db.commit()
    leave = (await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave.id))).scalar_one()
    logger.info("leave_refused", id=leave.id, by=current_user.username)
    return leave


# ---------------------------------------------------------------------------
# Appraisals
# ---------------------------------------------------------------------------
appraisals_router = APIRouter(prefix="/hr/appraisals")


@appraisals_router.get("", response_model=list[AppraisalRead])
async def list_appraisals(
    _: Annotated[User, Depends(require_appraisal_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Appraisal]:
    result = await db.execute(select(Appraisal).order_by(Appraisal.appraisal_date.desc(), Appraisal.id))
    return list(result.scalars().all())


@appraisals_router.post("", response_model=AppraisalRead, status_code=status.HTTP_201_CREATED)
async def create_appraisal(
    payload: AppraisalCreate,
    _: Annotated[User, Depends(require_appraisal_create)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Appraisal:
    await _get_or_404(db, Employee, payload.employee_id, "Employee")
    await _get_or_404(db, Employee, payload.manager_id, "Manager")

    appraisal = Appraisal(**payload.model_dump(), state=APPRAISAL_DRAFT)
    db.add(appraisal)
    await db.commit()
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal.id))
    ).scalar_one()
    logger.info("appraisal_created", employee_id=appraisal.employee_id)
    return appraisal


@appraisals_router.get("/{appraisal_id}", response_model=AppraisalRead)
async def get_appraisal(
    appraisal_id: int,
    _: Annotated[User, Depends(require_appraisal_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Appraisal:
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal_id))
    ).scalar_one_or_none()
    if appraisal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")
    return appraisal


@appraisals_router.patch("/{appraisal_id}", response_model=AppraisalRead)
async def update_appraisal(
    appraisal_id: int,
    payload: AppraisalUpdate,
    _: Annotated[User, Depends(require_appraisal_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Appraisal:
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal_id))
    ).scalar_one_or_none()
    if appraisal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "employee_id":
            if value is None:
                continue
            await _get_or_404(db, Employee, value, "Employee")
        elif field == "manager_id" and value is not None:
            await _get_or_404(db, Employee, value, "Manager")
        setattr(appraisal, field, value)

    await db.commit()
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal.id))
    ).scalar_one()
    logger.info("appraisal_updated", id=appraisal.id)
    return appraisal


@appraisals_router.delete("/{appraisal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appraisal(
    appraisal_id: int,
    _: Annotated[User, Depends(require_appraisal_unlink)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal_id))
    ).scalar_one_or_none()
    if appraisal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")

    await db.delete(appraisal)
    await db.commit()
    logger.info("appraisal_deleted", id=appraisal_id)


@appraisals_router.post("/{appraisal_id}/complete", response_model=AppraisalRead)
async def complete_appraisal(
    appraisal_id: int,
    _: Annotated[User, Depends(require_appraisal_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Appraisal:
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal_id))
    ).scalar_one_or_none()
    if appraisal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appraisal not found")
    if appraisal.state != APPRAISAL_DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft appraisals can be completed")
    if appraisal.final_rating is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="final_rating must be set before completing")

    appraisal.state = APPRAISAL_DONE

    await db.commit()
    appraisal = (
        await db.execute(select(Appraisal).where(Appraisal.id == appraisal.id))
    ).scalar_one()
    logger.info("appraisal_completed", id=appraisal.id)
    return appraisal


router.include_router(leave_types_router)
router.include_router(leaves_router)
router.include_router(appraisals_router)
