from typing import Any, Union
from sqlalchemy.orm import Session

from app.models.tenantprofile import TenantProfile
from app.schemas import user as schema_user
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError
from app.core.security import verify_password_hash, get_password_hash
from app.schemas.tenantprofile import TenantProfileCreate
from app.schemas.user import UserCreate, UserInternal
from app.services.lodge_service import is_tenant


def sign_up_user(
        user_data: Union[schema_user.UserCreate | TenantProfileCreate],
        db: Session,
        role: UserRole = UserRole.LANDLORD
):
    #rules:
    #don't store plain password
    #the user must not exist

    #steps
    #check if the user exist -> error
    user = crud_user.get_user_by_email(db, email=user_data.email)

    if user:
        raise UserAlreadyExistError(email=user_data.email)

    user_dict = user_data.model_dump()
    password = user_dict.pop('password')
    hashed = get_password_hash(password)

    if is_tenant(role):
        return crud_tenant.create_tenant(db, tenant_data=user_data, hashed_password=hashed, role=role)

    user_dict['hashed_password'] = hashed
    landlord_data = UserInternal.model_validate(user_dict)
    return crud_user.create(db, obj_in=landlord_data, role=role)
    #turn the user_data to a dictionary
    #remove the password key and value(save the value)
    #check the user's role -> tenant->
    #send the tenant data to the crud_tenant->
    # create the instance of the user using only the required fields from the tenant_data
    # set the user's role to tenant,save the hashed password
    #if not save the user normally-> send his role in,(landlord) and set the hashed password as well


    pass


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by checking their email and password.
    """
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password_hash(password, user.hashed_password):
        return None
    return user
