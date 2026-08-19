from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ModelAccess(Base):
    """Per-model CRUD permissions for a role, analogous to Odoo's ``ir.model.access``."""

    __tablename__ = "model_accesses"
    __table_args__ = (UniqueConstraint("role_id", "model", name="uq_model_access_role_model"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    perm_create: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_write: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_unlink: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    role: Mapped["Role"] = relationship(back_populates="model_accesses", lazy="selectin")  # noqa: F821

    @property
    def role_name(self) -> str:
        return self.role.name
