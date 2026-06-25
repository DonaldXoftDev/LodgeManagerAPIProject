from uuid import UUID

from sqlalchemy.orm import Session

from app.api.deps import get_db, get_landlord_user
from app.models.user import User
from app.schemas import invitation as schema_invite
from fastapi import APIRouter, Depends

from app.services import invite_service

router = APIRouter()

@router.post('/', response_model=schema_invite.InviteResponse)
def invite_tenant(
        invite_in: schema_invite.InviteCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)

):
    return invite_service.invite_tenant(db, invite_in=invite_in, landlord_id=landlord_user.id)

@router.get('/{invite_id}', response_model=schema_invite.InviteDetail)
def get_invite_by_id(
        invite_id: UUID,
        db: Session = Depends(get_db),
):
    return  invite_service.fetch_invite_record(db, invite_id=invite_id)