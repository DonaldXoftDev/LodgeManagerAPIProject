from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import InviteStatus


class InviteCreate(BaseModel):
    lodge_id: int
    expires_at:datetime


class InviteResponse(InviteCreate):
    id: UUID
    status: InviteStatus
    created_at: datetime

class InviteDetail(InviteResponse):
    lodge_name: str

