from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_root
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger(__name__)


async def _get_role(db: AsyncSession, name: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


@router.get("", response_model=list[UserRead])
async def list_users(
    current_user: Annotated[User, Depends(require_root)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: Annotated[User, Depends(require_root)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    existing = (
        await db.execute(select(User).where((User.username == payload.username) | (User.email == payload.email)))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    default_role = await _get_role(db, "user")
    if default_role is not None:
        user.roles.append(default_role)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("user_created", username=user.username)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_root)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: Annotated[User, Depends(require_root)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.email is not None:
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.password is not None:
        user.hashed_password = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role_names is not None:
        roles = []
        for name in payload.role_names:
            role = await _get_role(db, name)
            if role is not None:
                roles.append(role)
        user.roles = roles

    await db.commit()
    await db.refresh(user)
    logger.info("user_updated", username=user.username)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_root)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    await db.delete(user)
    await db.commit()
    logger.info("user_deleted", username=user.username)
