from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.schemas import tenantprofile as schema_tenant
from app.crud.tenantprofile import crud_tenant
from typing import List
from app.api.deps import get_db, get_current_user, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import tenant_services

router = APIRouter()


@router.patch('/profiles/me', response_model=schema_tenant.TenantProfileResponse)
def update_tenant_profile(
        tenant_data: schema_tenant.TenantProfileUpdate,
        db: Session = Depends(get_db),
        current_user: User =Depends(get_tenant_user)
):
    #TODO: Refactor the pydantic schemas for updating tenant profile vs user security profile
    try:
        return tenant_services.update_tenant_profile(
            db=db,
            update_data=tenant_data,
            base_user = current_user,
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get('/{tenant_id}', response_model=schema_tenant.TenantProfileResponse)
def get_tenant_by_id(
        tenant_id: int,
        db: Session = Depends(get_db),
        tenant_user=Depends(get_current_user)
):
    tenant = crud_tenant.g
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )
    return tenant


@router.delete('/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_by_id(
        tenant_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    #is logged user a tenant..
    #
    tenant = crud_tenant

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )

    crud_tenant.delete_tenant(db=db, db_tenant=tenant)

