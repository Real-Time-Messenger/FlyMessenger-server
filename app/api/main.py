from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.dialogs import router as dialogs_router
from app.api.endpoints.search import router as search_router

router = APIRouter()

router.include_router(auth_router, tags=["auth"], prefix="/auth")
router.include_router(users_router, tags=["users"], prefix="/users")
router.include_router(dialogs_router, tags=["dialogs"], prefix="/dialogs")
router.include_router(search_router, tags=["search"], prefix="/search")