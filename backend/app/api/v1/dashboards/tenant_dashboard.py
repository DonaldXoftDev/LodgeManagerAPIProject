"""
API routes for tenant dashboards.

Provides endpoints to retrieve dashboard statistics and summaries for tenants.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_tenant_user
from app.models.user import User
from app.schemas.dashboard import TenantDashboardStats
from app.services import  dashboard_service


router = APIRouter()

@router.get('/me/tenants', response_model=list[TenantDashboardStats])
def get_tenant_dashboard_stat(
        skip: int | None = None,
        limit: int | None = None,
        db: Session =Depends(get_db),
        current_user : User = Depends(get_tenant_user)
):
    return dashboard_service.get_tenant_active_lease_stats(
        db,
        skip=skip,
        limit=limit,
        tenant_id= current_user.tenant_profile.id,
        lodge_id=current_user.tenant_profile.lodge_id
    )
