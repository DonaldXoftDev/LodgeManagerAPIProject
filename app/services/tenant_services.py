from sqlalchemy.orm import Session
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError
from app.core.security import  get_password_hash
from app.schemas.tenantprofile import TenantProfileCreate
from app.schemas.user import UserInternal

def sign_up_tenant(
        db: Session,
        tenant_in: TenantProfileCreate,
):
    if crud_user.get_user_by_email(db, email=tenant_in.user_info.email):
        raise UserAlreadyExistError(email=tenant_in.user_info.email)

    hashed = get_password_hash(tenant_in.user_info.password)

    base_user_data = UserInternal(
        first_name=tenant_in.user_info.first_name,
        last_name=tenant_in.user_info.last_name,
        phone_no=tenant_in.user_info.phone_no,
        email=tenant_in.user_info.email,
        hashed_password=hashed,
        role=UserRole.TENANT
    )

    return crud_tenant.create_tenant(db, tenant_in=tenant_in, internal_user=base_user_data)