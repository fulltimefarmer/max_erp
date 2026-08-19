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
