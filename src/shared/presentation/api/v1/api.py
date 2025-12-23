from fastapi import APIRouter

from src.account.presentation.api.v1.endpoints import router as account_router
from src.compliance.endpoints import router as compliance_router
from src.notification.presentation.api.v1.endpoints import router as notification_router
from src.shared.presentation.api.v1.tenant_endpoints import router as tenant_router

api_router = APIRouter()

api_router.include_router(account_router, prefix="/account", tags=["account"])
api_router.include_router(
    notification_router, prefix="/notification", tags=["notification"]
)
api_router.include_router(tenant_router, prefix="/tenants", tags=["tenants"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["compliance"])
