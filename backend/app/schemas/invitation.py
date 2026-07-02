from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import InviteStatus


class InviteCreate(BaseModel):
    lodge_id: int
    expires_at:datetime


class InviteResponse(InviteCreate):
    id: UUID
    lodge_id: int
    status: InviteStatus
    created_at: datetime
    is_expired: bool

class InviteDetail(InviteResponse):
    lodge_name: str

