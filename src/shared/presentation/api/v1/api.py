from fastapi import APIRouter

from src.account.presentation.api.v1.endpoints import router as account_router
from src.notification.presentation.api.v1.endpoints import router as notification_router

api_router = APIRouter()

api_router.include_router(account_router, prefix="/account", tags=["account"])
api_router.include_router(
    notification_router, prefix="/notification", tags=["notification"]
)
