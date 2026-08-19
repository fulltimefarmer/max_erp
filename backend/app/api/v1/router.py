from fastapi import APIRouter

from app.api.v1 import auth, health, hr, menus, model_access, pages, permissions, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(menus.router)
api_router.include_router(pages.router)
api_router.include_router(model_access.router)
api_router.include_router(permissions.router)
api_router.include_router(hr.router)
