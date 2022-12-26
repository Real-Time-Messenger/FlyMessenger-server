from fastapi import APIRouter
from app.api.endpoints.test.endpoints.auth import router as test_auth_router

router = APIRouter()

"""
Include all testing endpoints.
"""
router.include_router(test_auth_router, prefix="/auth")