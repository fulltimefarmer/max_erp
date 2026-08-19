from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_model_access
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.model_access import ModelAccess
from app.models.role import Role
from app.models.user import User
from app.schemas.access import ModelAccessRead, ModelAccessUpsert

router = APIRouter(prefix="/model-accesses", tags=["model-access"])
logger = get_logger(__name__)

require_access_write = require_model_access("ir.model.access", "write")
require_access_read = require_model_access("ir.model.access", "read")


@router.get("", response_model=list[ModelAccessRead])
async def list_model_accesses(
    _: Annotated[User, Depends(require_access_read)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ModelAccess]:
    result = await db.execute(select(ModelAccess).order_by(ModelAccess.model, ModelAccess.role_id))
    return list(result.scalars().all())


@router.put("", response_model=ModelAccessRead)
async def upsert_model_access(
    payload: ModelAccessUpsert,
    _: Annotated[User, Depends(require_access_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModelAccess:
    role = (
        await db.execute(select(Role).where(Role.name == payload.role_name))
    ).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    access = (
        await db.execute(
            select(ModelAccess).where(
                ModelAccess.model == payload.model,
                ModelAccess.role_id == role.id,
            )
        )
    ).scalar_one_or_none()

    if access is None:
        access = ModelAccess(model=payload.model, role_id=role.id)
        db.add(access)

    access.perm_create = payload.perm_create
    access.perm_read = payload.perm_read
    access.perm_write = payload.perm_write
    access.perm_unlink = payload.perm_unlink

    await db.commit()
    # Re-load so the selectin `role` relationship is populated for serialization.
    access = (
        await db.execute(select(ModelAccess).where(ModelAccess.id == access.id))
    ).scalar_one()
    logger.info("model_access_upserted", model=access.model, role=role.name)
    return access


@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_access(
    access_id: int,
    _: Annotated[User, Depends(require_access_write)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    access = (
        await db.execute(select(ModelAccess).where(ModelAccess.id == access_id))
    ).scalar_one_or_none()
    if access is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model access not found")

    await db.delete(access)
    await db.commit()
    logger.info("model_access_deleted", id=access_id)
