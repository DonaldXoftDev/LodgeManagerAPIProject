from app.schemas.user import UserCreate
from typing import Optional
from app.core.enums import TenantType
from pydantic import EmailStr, Field


class TenantBase(UserCreate):
    tenant_type: TenantType


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantCreate):
    id: int
    is_active: bool
    created_at: datetime
    role: UserRole

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_no: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
