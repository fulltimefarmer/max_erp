from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import Menu
from app.models.model_access import ModelAccess
from app.models.page import Page
from app.models.role import Role
from app.models.user import User

# Role that bypasses every access check (the Odoo superuser equivalent).
SUPERUSER_ROLE = "root"

# Canonical model registry. Every model that can be protected by ModelAccess
# must be listed here so that seeding and permission summaries stay in sync.
MODEL_NAMES = [
    "res.users",
    "res.roles",
    "ir.menu",
    "ir.page",
    "ir.model.access",
]

PERMISSIONS = ("create", "read", "write", "unlink")


def _role_ids(user: User) -> list[int]:
    return [role.id for role in user.roles]


def _is_superuser(user: User) -> bool:
    return any(role.name == SUPERUSER_ROLE for role in user.roles)


async def has_model_access(
    db: AsyncSession, user: User, model: str, operation: str
) -> bool:
    """Return True if the user may perform ``operation`` on ``model``.

    Access is the union of the permissions granted by every role the user
    holds. The superuser role always has full access.
    """
    if operation not in PERMISSIONS:
        raise ValueError(f"Unknown operation: {operation}")
    if _is_superuser(user):
        return True

    role_ids = _role_ids(user)
    if not role_ids:
        return False

    column = getattr(ModelAccess, f"perm_{operation}")
    result = await db.execute(
        select(column).where(
            ModelAccess.model == model,
            ModelAccess.role_id.in_(role_ids),
        )
    )
    return any(result.scalars().all())


async def has_menu_access(db: AsyncSession, user: User, code: str) -> bool:
    """Return True if the user can see the menu identified by ``code``."""
    if _is_superuser(user):
        return True

    role_ids = _role_ids(user)
    if not role_ids:
        return False

    result = await db.execute(
        select(Menu.id).where(
            Menu.code == code,
            Menu.active.is_(True),
            Menu.roles.any(Role.id.in_(role_ids)),
        )
    )
    return result.scalar_one_or_none() is not None


async def has_page_access(db: AsyncSession, user: User, code: str) -> bool:
    """Return True if the user can access the page identified by ``code``."""
    if _is_superuser(user):
        return True

    role_ids = _role_ids(user)
    if not role_ids:
        return False

    result = await db.execute(
        select(Page.id).where(
            Page.code == code,
            Page.active.is_(True),
            Page.roles.any(Role.id.in_(role_ids)),
        )
    )
    return result.scalar_one_or_none() is not None


async def get_accessible_menus(db: AsyncSession, user: User) -> list[Menu]:
    if _is_superuser(user):
        result = await db.execute(
            select(Menu).where(Menu.active.is_(True)).order_by(Menu.sequence, Menu.id)
        )
        return list(result.scalars().all())

    role_ids = _role_ids(user)
    if not role_ids:
        return []

    result = await db.execute(
        select(Menu)
        .where(Menu.active.is_(True), Menu.roles.any(Role.id.in_(role_ids)))
        .order_by(Menu.sequence, Menu.id)
    )
    return list(result.scalars().all())


async def get_accessible_pages(db: AsyncSession, user: User) -> list[Page]:
    if _is_superuser(user):
        result = await db.execute(
            select(Page).where(Page.active.is_(True)).order_by(Page.id)
        )
        return list(result.scalars().all())

    role_ids = _role_ids(user)
    if not role_ids:
        return []

    result = await db.execute(
        select(Page)
        .where(Page.active.is_(True), Page.roles.any(Role.id.in_(role_ids)))
        .order_by(Page.id)
    )
    return list(result.scalars().all())


async def get_model_access_map(
    db: AsyncSession, user: User
) -> dict[str, dict[str, bool]]:
    """Return ``{model: {create, read, write, unlink}}`` for the user.

    For the superuser every registered model is fully permitted.
    """
    if _is_superuser(user):
        return {
            model: {op: True for op in PERMISSIONS} for model in MODEL_NAMES
        }

    role_ids = _role_ids(user)
    result = await db.execute(
        select(ModelAccess).where(ModelAccess.role_id.in_(role_ids))
    )
    accesses = result.scalars().all()

    mapping: dict[str, dict[str, bool]] = {}
    for access in accesses:
        perms = mapping.setdefault(
            access.model, {op: False for op in PERMISSIONS}
        )
        for op in PERMISSIONS:
            perms[op] = perms[op] or getattr(access, f"perm_{op}")
    return mapping
