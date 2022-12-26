from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.dialogs import router as dialogs_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.test.main import router as test_router

router = APIRouter()

"""
Load all endpoints in one router for easy import.
"""
router.include_router(auth_router, tags=["Authentication"], prefix="/auth")
router.include_router(users_router, tags=["Users"], prefix="/users")
router.include_router(dialogs_router, tags=["Dialogs"], prefix="/dialogs")
router.include_router(search_router, tags=["Search"], prefix="/search")
router.include_router(test_router, tags=["Test"], prefix="/test")