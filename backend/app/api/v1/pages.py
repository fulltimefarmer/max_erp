from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_model_access
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.page import Page
from app.models.role import Role
from app.models.user import User
from app.schemas.access import PageCreate, PageRead, PageUpdate, RoleAssignment

router = APIRouter(prefix="/pages", tags=["pages"])
logger = get_logger(__name__)

require_page_write = require_model_access("ir.page", "write")
require_page_read = require_model_access("ir.page", "read")


async def _get_roles_by_name(db: AsyncSession, names: list[str]) -> list[Role]:
    result = await db.execute(select(Role).where(Role.name.in_(names)))
    return list(result.scalars().all())


@router.get("", response_model=list[PageRead])
async def list_pages(
    _: Annotated[User, Depends(require_page_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Page]:
    result = await db.execute(select(Page).order_by(Page.id))
    return list(result.scalars().all())


@router.post("", response_model=PageRead, status_code=status.HTTP_201_CREATED)
async def create_page(
    payload: PageCreate,
    _: Annotated[User, Depends(require_page_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    existing = (
        await db.execute(select(Page).where(Page.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Page code already exists")

    page = Page(**payload.model_dump())
    db.add(page)
    await db.commit()
    page = (await db.execute(select(Page).where(Page.id == page.id))).scalar_one()
    logger.info("page_created", code=page.code)
    return page


@router.get("/{page_id}", response_model=PageRead)
async def get_page(
    page_id: int,
    _: Annotated[User, Depends(require_page_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    page = (await db.execute(select(Page).where(Page.id == page_id))).scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return page


@router.patch("/{page_id}", response_model=PageRead)
async def update_page(
    page_id: int,
    payload: PageUpdate,
    _: Annotated[User, Depends(require_page_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    page = (await db.execute(select(Page).where(Page.id == page_id))).scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(page, field, value)

    await db.commit()
    page = (await db.execute(select(Page).where(Page.id == page.id))).scalar_one()
    logger.info("page_updated", code=page.code)
    return page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: int,
    _: Annotated[User, Depends(require_page_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    page = (await db.execute(select(Page).where(Page.id == page_id))).scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    await db.delete(page)
    await db.commit()
    logger.info("page_deleted", code=page.code)


@router.put("/{page_id}/roles", response_model=PageRead)
async def set_page_roles(
    page_id: int,
    payload: RoleAssignment,
    _: Annotated[User, Depends(require_page_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Page:
    page = (await db.execute(select(Page).where(Page.id == page_id))).scalar_one_or_none()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    page.roles = await _get_roles_by_name(db, payload.role_names)
    await db.commit()
    page = (await db.execute(select(Page).where(Page.id == page.id))).scalar_one()
    logger.info("page_roles_updated", code=page.code, roles=payload.role_names)
    return page
