from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_model_access
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User
from app.schemas.access import MenuCreate, MenuRead, MenuUpdate, RoleAssignment

router = APIRouter(prefix="/menus", tags=["menus"])
logger = get_logger(__name__)

require_menu_write = require_model_access("ir.menu", "write")
require_menu_read = require_model_access("ir.menu", "read")


async def _get_roles_by_name(db: AsyncSession, names: list[str]) -> list[Role]:
    result = await db.execute(select(Role).where(Role.name.in_(names)))
    return list(result.scalars().all())


@router.get("", response_model=list[MenuRead])
async def list_menus(
    _: Annotated[User, Depends(require_menu_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Menu]:
    result = await db.execute(select(Menu).order_by(Menu.sequence, Menu.id))
    return list(result.scalars().all())


@router.post("", response_model=MenuRead, status_code=status.HTTP_201_CREATED)
async def create_menu(
    payload: MenuCreate,
    _: Annotated[User, Depends(require_menu_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Menu:
    existing = (
        await db.execute(select(Menu).where(Menu.code == payload.code))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Menu code already exists")

    menu = Menu(**payload.model_dump())
    db.add(menu)
    await db.commit()
    menu = (await db.execute(select(Menu).where(Menu.id == menu.id))).scalar_one()
    logger.info("menu_created", code=menu.code)
    return menu


@router.get("/{menu_id}", response_model=MenuRead)
async def get_menu(
    menu_id: int,
    _: Annotated[User, Depends(require_menu_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Menu:
    menu = (await db.execute(select(Menu).where(Menu.id == menu_id))).scalar_one_or_none()
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return menu


@router.patch("/{menu_id}", response_model=MenuRead)
async def update_menu(
    menu_id: int,
    payload: MenuUpdate,
    _: Annotated[User, Depends(require_menu_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Menu:
    menu = (await db.execute(select(Menu).where(Menu.id == menu_id))).scalar_one_or_none()
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(menu, field, value)

    await db.commit()
    menu = (await db.execute(select(Menu).where(Menu.id == menu.id))).scalar_one()
    logger.info("menu_updated", code=menu.code)
    return menu


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: int,
    _: Annotated[User, Depends(require_menu_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    menu = (await db.execute(select(Menu).where(Menu.id == menu_id))).scalar_one_or_none()
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    await db.delete(menu)
    await db.commit()
    logger.info("menu_deleted", code=menu.code)


@router.put("/{menu_id}/roles", response_model=MenuRead)
async def set_menu_roles(
    menu_id: int,
    payload: RoleAssignment,
    _: Annotated[User, Depends(require_menu_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Menu:
    menu = (await db.execute(select(Menu).where(Menu.id == menu_id))).scalar_one_or_none()
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    menu.roles = await _get_roles_by_name(db, payload.role_names)
    await db.commit()
    menu = (await db.execute(select(Menu).where(Menu.id == menu.id))).scalar_one()
    logger.info("menu_roles_updated", code=menu.code, roles=payload.role_names)
    return menu
