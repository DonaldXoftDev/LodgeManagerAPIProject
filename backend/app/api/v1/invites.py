from uuid import UUID

from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_db, get_landlord_user
from app.models.user import User
from app.schemas import invitation as schema_invite
from fastapi import APIRouter, Depends
from app.schemas.error import ErrorResponseSchema

from app.services import invite_service

router = APIRouter()

@router.post(
    '/',
    response_model=schema_invite.InviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tenant invitation",
    description=(
        "Generates a new invitation link for a prospective tenant. "
        "The lodge must belong to the authenticated landlord."
    ),
    response_description="The created invitation with its UUID link",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Lodge does not exist or does not belong to the authenticated landlord"},
    },
)
def invite_tenant(
        invite_in: schema_invite.InviteCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)

):
    return invite_service.invite_tenant(db, invite_in=invite_in, landlord_id=landlord_user.id)

@router.get(
    '/{invite_id}',
    response_model=schema_invite.InviteDetail,
    summary="Get invitation details",
    description=(
        "Retrieves the details of a specific invitation. "
        "This is a public endpoint used by prospective tenants to view their invitation."
    ),
    response_description="Invitation details including lodge name and expiry status",
    responses={
        404: {"model": ErrorResponseSchema, "description": "The invitation ID does not exist"},
    },
)
def get_invite_by_id(
        invite_id: UUID,
        db: Session = Depends(get_db),
):
    return  invite_service.fetch_invite_record(db, invite_id=invite_id)