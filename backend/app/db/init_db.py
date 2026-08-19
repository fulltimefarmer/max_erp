from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User

logger = get_logger(__name__)

DEFAULT_ROLES = [
    ("root", "Super administrator with full access to all resources"),
    ("user", "Standard user with limited access"),
]


async def init_db() -> None:
    """Seed default roles and the root account on startup."""
    async with async_session_factory() as session:
        existing_role_names = set((await session.execute(select(Role.name))).scalars().all())
        for name, description in DEFAULT_ROLES:
            if name not in existing_role_names:
                session.add(Role(name=name, description=description))
        await session.commit()

        root_role = (await session.execute(select(Role).where(Role.name == "root"))).scalar_one()

        root = (
            await session.execute(select(User).where(User.username == settings.root_username))
        ).scalar_one_or_none()

        if root is None:
            root = User(
                username=settings.root_username,
                email=settings.root_email,
                hashed_password=hash_password(settings.root_password),
                is_active=True,
            )
            root.roles.append(root_role)
            session.add(root)
            await session.commit()
            logger.info("root_user_created", username=settings.root_username)
        else:
            role_names = {role.name for role in root.roles}
            if "root" not in role_names:
                root.roles.append(root_role)
                await session.commit()
                logger.info("root_role_attached", username=settings.root_username)
