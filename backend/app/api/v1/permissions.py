from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core import access
from app.core.database import get_db
from app.models.user import User
from app.schemas.access import MenuRead, ModelAccessSummary, PageRead, Permissions

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/me", response_model=Permissions)
async def my_permissions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Permissions:
    """Return the menus, pages and model access granted to the current user."""
    menus = await access.get_accessible_menus(db, current_user)
    pages = await access.get_accessible_pages(db, current_user)
    model_map = await access.get_model_access_map(db, current_user)

    summaries = [
        ModelAccessSummary(
            model=model,
            create=perms["create"],
            read=perms["read"],
            write=perms["write"],
            unlink=perms["unlink"],
        )
        for model, perms in sorted(model_map.items())
    ]

    return Permissions(
        menus=[MenuRead.model_validate(m) for m in menus],
        pages=[PageRead.model_validate(p) for p in pages],
        model_accesses=summaries,
    )
