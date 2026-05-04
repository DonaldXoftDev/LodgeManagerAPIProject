from datetime import datetime

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from typing import Optional
from app.core.enums import TenantType, StudentLevel, UserRole
from pydantic import EmailStr, Field, BaseModel


class TenantBase(UserCreate):
    tenant_type: TenantType
    emergency_contact_name: str
    emergency_contact_phone_no: str
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None


class TenantProfileCreate(TenantBase):
    pass


class TenantProfileResponse(BaseModel):
    id: int
    is_active: bool
    created_at: datetime
    role: UserRole
    user: UserResponse

    model_config = {'from_attributes': True}


class TenantProfileUpdate(UserUpdate):
    tenant_type: Optional[TenantType] = None
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None
