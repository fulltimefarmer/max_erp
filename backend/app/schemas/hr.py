from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DepartmentBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    parent_id: int | None = None
    active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    parent_id: int | None = None
    active: bool | None = None


class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class JobPositionBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    department_id: int | None = None
    active: bool = True


class JobPositionCreate(JobPositionBase):
    pass


class JobPositionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, max_length=50)
    department_id: int | None = None
    active: bool | None = None


class JobPositionRead(JobPositionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmployeeBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    work_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    hire_date: date | None = None
    job_id: int | None = None
    department_id: int | None = None
    manager_id: int | None = None
    user_id: int | None = None
    active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    work_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    hire_date: date | None = None
    job_id: int | None = None
    department_id: int | None = None
    manager_id: int | None = None
    user_id: int | None = None
    active: bool | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    job_name: str | None = None
    department_name: str | None = None
    manager_name: str | None = None


class LeaveTypeBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    allowance_days: int = Field(default=0, ge=0)
    active: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeRead(LeaveTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type_id: int
    date_from: date
    date_to: date
    description: str | None = None


class LeaveRequestUpdate(BaseModel):
    employee_id: int | None = None
    leave_type_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    description: str | None = None


class LeaveRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_type_id: int
    date_from: date
    date_to: date
    number_of_days: int
    state: str
    description: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    employee_name: str = ""
    leave_type_name: str = ""


class AppraisalCreate(BaseModel):
    employee_id: int
    manager_id: int | None = None
    appraisal_date: date
    final_rating: int | None = Field(default=None, ge=1, le=5)
    goals: str | None = None
    feedback: str | None = None


class AppraisalUpdate(BaseModel):
    employee_id: int | None = None
    manager_id: int | None = None
    appraisal_date: date | None = None
    final_rating: int | None = Field(default=None, ge=1, le=5)
    goals: str | None = None
    feedback: str | None = None


class AppraisalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    manager_id: int | None = None
    appraisal_date: date
    final_rating: int | None = None
    state: str
    goals: str | None = None
    feedback: str | None = None
    created_at: datetime
    employee_name: str = ""
    manager_name: str | None = None
