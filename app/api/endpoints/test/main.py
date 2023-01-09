from fastapi import APIRouter
from app.api.endpoints.test.endpoints.auth import router as test_auth_router
from app.api.endpoints.test.endpoints.dialogs import router as test_dialogs_router

router = APIRouter()

"""
Include all testing endpoints.
"""
router.include_router(test_auth_router, prefix="/auth")
router.include_router(test_dialogs_router, prefix="/dialogs")
