from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import MODEL_NAMES
from app.core.config import settings
from app.core.database import async_session_factory
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.menu import Menu
from app.models.model_access import ModelAccess
from app.models.page import Page
from app.models.role import Role
from app.models.user import User

logger = get_logger(__name__)

DEFAULT_ROLES = [
    ("root", "Super administrator with full access to all resources"),
    ("manager", "Manager with access to sales and inventory"),
    ("user", "Standard user with limited access"),
]

# (code, name, parent_code, sequence, icon, role_names)
MENU_SEED = [
    ("dashboard", "Dashboard", None, 10, None, ["root", "manager", "user"]),
    ("sales", "Sales", None, 20, None, ["root", "manager"]),
    ("sales.orders", "Sales Orders", "sales", 10, None, ["root", "manager"]),
    ("inventory", "Inventory", None, 30, None, ["root", "manager"]),
    ("inventory.products", "Products", "inventory", 10, None, ["root", "manager"]),
    ("accounting", "Accounting", None, 40, None, ["root"]),
    ("settings", "Settings", None, 50, None, ["root"]),
    ("settings.users", "Users", "settings", 10, None, ["root"]),
    ("settings.access", "Access Rights", "settings", 20, None, ["root"]),
]

# (code, name, route, role_names)
PAGE_SEED = [
    ("dashboard", "Dashboard", "/dashboard", ["root", "manager", "user"]),
    ("sales.orders", "Sales Orders", "/sales/orders", ["root", "manager"]),
    ("inventory.products", "Products", "/inventory/products", ["root", "manager"]),
    ("accounting", "Accounting", "/accounting", ["root"]),
    ("settings.users", "Users", "/settings/users", ["root"]),
    ("settings.access", "Access Rights", "/settings/access", ["root"]),
]

# (role_name, model, create, read, write, unlink)
MODEL_ACCESS_SEED = [
    ("manager", "res.users", True, True, True, False),
    ("manager", "res.roles", False, True, False, False),
    ("manager", "ir.menu", False, True, True, False),
    ("manager", "ir.page", False, True, True, False),
    ("manager", "ir.model.access", False, True, False, False),
    ("user", "res.users", False, True, False, False),
]


async def _roles_by_name(db: AsyncSession) -> dict[str, Role]:
    result = await db.execute(select(Role))
    return {role.name: role for role in result.scalars().all()}


async def _seed_roles(db: AsyncSession) -> None:
    existing = set((await db.execute(select(Role.name))).scalars().all())
    for name, description in DEFAULT_ROLES:
        if name not in existing:
            db.add(Role(name=name, description=description))


async def _seed_menus(db: AsyncSession, roles: dict[str, Role]) -> None:
    menu_by_code = {
        menu.code: menu for menu in (await db.execute(select(Menu))).scalars().all()
    }
    for code, name, parent_code, sequence, icon, role_names in MENU_SEED:
        menu = menu_by_code.get(code)
        if menu is None:
            menu = Menu(code=code, name=name, sequence=sequence, icon=icon)
            db.add(menu)
        else:
            menu.name = name
            menu.sequence = sequence
            menu.icon = icon

        menu.parent = menu_by_code.get(parent_code) if parent_code else None
        menu.roles = [roles[role_name] for role_name in role_names]
        menu_by_code[code] = menu


async def _seed_pages(db: AsyncSession, roles: dict[str, Role]) -> None:
    page_by_code = {
        page.code: page for page in (await db.execute(select(Page))).scalars().all()
    }
    for code, name, route, role_names in PAGE_SEED:
        page = page_by_code.get(code)
        if page is None:
            page = Page(code=code, name=name, route=route)
            db.add(page)
        else:
            page.name = name
            page.route = route

        page.roles = [roles[role_name] for role_name in role_names]
        page_by_code[code] = page


async def _seed_model_accesses(db: AsyncSession, roles: dict[str, Role]) -> None:
    existing = {
        (access.model, access.role_id): access
        for access in (await db.execute(select(ModelAccess))).scalars().all()
    }

    seeds: list[tuple[str, str, bool, bool, bool, bool]] = []
    # The superuser role has full access to every registered model.
    seeds.extend(("root", model, True, True, True, True) for model in MODEL_NAMES)
    seeds.extend(MODEL_ACCESS_SEED)

    for role_name, model, create, read, write, unlink in seeds:
        role = roles[role_name]
        key = (model, role.id)
        access = existing.get(key)
        if access is None:
            access = ModelAccess(model=model, role_id=role.id)
            db.add(access)
        access.perm_create = create
        access.perm_read = read
        access.perm_write = write
        access.perm_unlink = unlink


async def seed_rbac(db: AsyncSession) -> None:
    """Seed roles, menus, pages and model access into the given session.

    Idempotent: existing rows are updated in place rather than duplicated.
    """
    await _seed_roles(db)
    await db.flush()

    roles = await _roles_by_name(db)

    await _seed_menus(db, roles)
    await _seed_pages(db, roles)
    await _seed_model_accesses(db, roles)
    await db.flush()


async def seed_root_user(db: AsyncSession) -> None:
    """Ensure the superuser account from settings exists and holds the root role."""
    roles = await _roles_by_name(db)
    root = (
        await db.execute(select(User).where(User.username == settings.root_username))
    ).scalar_one_or_none()

    if root is None:
        root = User(
            username=settings.root_username,
            email=settings.root_email,
            hashed_password=hash_password(settings.root_password),
            is_active=True,
        )
        root.roles.append(roles["root"])
        db.add(root)
        logger.info("root_user_created", username=settings.root_username)
    elif "root" not in {role.name for role in root.roles}:
        root.roles.append(roles["root"])


async def init_db() -> None:
    """Seed default roles, menus, pages, model access and the root account."""
    async with async_session_factory() as session:
        await seed_rbac(session)
        await seed_root_user(session)
        await session.commit()
        logger.info(
            "rbac_seeded",
            roles=len(DEFAULT_ROLES),
            menus=len(MENU_SEED),
            pages=len(PAGE_SEED),
            model_accesses=len(MODEL_ACCESS_SEED) + len(MODEL_NAMES),
        )
