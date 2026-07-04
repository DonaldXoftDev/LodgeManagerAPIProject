"""
API routes for landlord dashboards.

Provides endpoints to retrieve dashboard statistics and summaries for landlords.
"""
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.api.deps import get_landlord_user, get_db
from app.core.enums import RoomStatus, BadgeTexts
from app.models.user import User
from app.schemas import dashboard as schema_dashboard
from app.schemas.dashboard import DashboardFilters, RoomLeaseInfo
from app.schemas.error import ErrorResponseSchema
from app.services import dashboard_service


router = APIRouter()




@router.get(
    '/me/landlord/{lodge_id}',
    response_model=schema_dashboard.LandlordDashboardStats,
    summary="Get landlord dashboard statistics",
    description=(
        "Retrieves comprehensive dashboard statistics for a specific lodge "
        "including financials, entity counts, and room occupancy breakdown."
    ),
    response_description="Complete dashboard statistics",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Lodge does not exist or does not belong to the authenticated landlord"},
    },
)
def get_landlord_dashboard(
        lodge_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        room_statuses: list[RoomStatus] = Query(default=[]),
        financial_filters: list[BadgeTexts] = Query(default=[]),
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user),

):
    """
    Retrieve dashboard statistics for a specific lodge.

    Args:
        lodge_id (int): The ID of the lodge.
        room_statuses (list[RoomStatus]): Optional list of room statuses to filter by.
        financial_filters (list[BadgeTexts]): Optional list of financial filters to apply.
        skip (int | None): Number of records to skip.
        limit (int | None): Maximum number of records to return.
        db (Session): The database session.
        landlord_user (User): The authenticated landlord user.

    Returns:
        schema_dashboard.LandlordDashboardStats: The aggregated dashboard statistics.
    """
    #goal: to get a list of landlord dashboard stats with
    #financial summary, total entities count, dictionary of dashboard rooms categories
    # that match a specific filter and is paginated
    #does the lodge exist and is owned by the landlord??
    all_filters = DashboardFilters(
        room_status_filters= room_statuses,
        financial_filters=financial_filters
    )
    return dashboard_service.get_landlord_dashboard(
        db, lodge_id=lodge_id,skip=skip,limit=limit,
        filter_by=all_filters, landlord_id=landlord_user.id
    )


@router.get(
    '/lease-info/{lease_id}',
    response_model=RoomLeaseInfo,
    summary="Get detailed room lease info",
    description=(
        "Retrieves detailed information about a specific lease "
        "including room details, tenant info, and financial breakdown."
    ),
    response_description="Detailed room-lease-tenant-financial summary",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Lease does not exist or has no associated data"},
    },
)
def get_room_lease_info(
        lease_id: int,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    return dashboard_service.get_dashboard_lease_info(
        db,
        lease_id=lease_id,
        landlord_id=landlord_user.id
    )