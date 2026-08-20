from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Department(Base):
    """An HR department, analogous to Odoo's ``hr.department``."""

    __tablename__ = "hr_departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent: Mapped["Department | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Department"]] = relationship(back_populates="parent")


class JobPosition(Base):
    """A job position, analogous to Odoo's ``hr.job``."""

    __tablename__ = "hr_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    department: Mapped["Department | None"] = relationship(lazy="selectin")


class Employee(Base):
    """An employee record, analogous to Odoo's ``hr.employee``."""

    __tablename__ = "hr_employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    work_email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    job_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_jobs.id", ondelete="SET NULL"), nullable=True
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True
    )
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_employees.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped["JobPosition | None"] = relationship(lazy="selectin")
    department: Mapped["Department | None"] = relationship(lazy="selectin")
    manager: Mapped["Employee | None"] = relationship(remote_side=[id], lazy="selectin")

    @property
    def job_name(self) -> str | None:
        return self.job.name if self.job else None

    @property
    def department_name(self) -> str | None:
        return self.department.name if self.department else None

    @property
    def manager_name(self) -> str | None:
        return self.manager.name if self.manager else None


class LeaveType(Base):
    """A leave type (e.g. annual, sick), analogous to Odoo's ``hr.leave.type``."""

    __tablename__ = "hr_leave_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    allowance_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LeaveRequest(Base):
    """A leave/time-off request, analogous to Odoo's ``hr.leave``."""

    __tablename__ = "hr_leaves"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_type_id: Mapped[int] = mapped_column(
        ForeignKey("hr_leave_types.id", ondelete="RESTRICT"), nullable=False
    )
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    number_of_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    state: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    employee: Mapped["Employee"] = relationship(lazy="selectin")
    leave_type: Mapped["LeaveType"] = relationship(lazy="selectin")

    @property
    def employee_name(self) -> str:
        return self.employee.name

    @property
    def leave_type_name(self) -> str:
        return self.leave_type.name


class Appraisal(Base):
    """An employee performance appraisal, analogous to Odoo's ``hr.appraisal``."""

    __tablename__ = "hr_appraisals"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("hr_employees.id", ondelete="SET NULL"), nullable=True
    )
    appraisal_date: Mapped[date] = mapped_column(Date, nullable=False)
    final_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    employee: Mapped["Employee"] = relationship(foreign_keys=[employee_id], lazy="selectin")
    manager: Mapped["Employee | None"] = relationship(
        foreign_keys=[manager_id], lazy="selectin"
    )

    @property
    def employee_name(self) -> str:
        return self.employee.name

    @property
    def manager_name(self) -> str | None:
        return self.manager.name if self.manager else None
