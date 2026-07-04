"""
API routes for tenant dashboards.

Provides endpoints to retrieve dashboard statistics and summaries for tenants.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_tenant_user
from app.models.user import User
from app.schemas.dashboard import TenantDashboardStats
from app.schemas.error import ErrorResponseSchema
from app.services import  dashboard_service


router = APIRouter()

@router.get(
    '/me/tenants',
    response_model=list[TenantDashboardStats],
    summary="Get tenant dashboard statistics",
    description=(
        "Retrieves dashboard statistics for the authenticated tenant "
        "including active lease summaries, room details, and financial breakdown."
    ),
    response_description="List of active lease statistics for the tenant",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only tenant accounts can perform this action"},
    },
)
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
