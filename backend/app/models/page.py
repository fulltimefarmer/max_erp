from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

role_pages = Table(
    "role_pages",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("page_id", ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True),
)


class Page(Base):
    """A frontend page/route, analogous to an Odoo view action."""

    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    route: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        secondary=role_pages, back_populates="pages", lazy="selectin"
    )

    @property
    def role_names(self) -> list[str]:
        return [role.name for role in self.roles]
