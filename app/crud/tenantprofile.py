from app.core.enums import UserRole
from app.core.security import get_password_hash
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate
from sqlalchemy.orm import Session, joinedload
from app.crud.base_crud import CRUDBase
from app.schemas.user import UserCreate


class CRUDTenantProfile(CRUDBase[TenantProfile, TenantProfileCreate, TenantProfileUpdate]):
    def create_tenant(self, db: Session, *, tenant_data: TenantProfileCreate, hashed_password: str, role:UserRole):
        try:
            user_dict = {k:v for k,v in tenant_data.model_dump().items() if k in User.__table__.columns}
            user_dict['hashed_password'] = hashed_password
            user_dict['role'] = role

            db_user = User(**user_dict)
            db.add(db_user)
            db.flush()

            tenant_dict = {k:v for k,v in tenant_data.model_dump().items() if k in TenantProfile.__table__.columns}
            db_tenant = TenantProfile(**tenant_dict, user_id=db_user.id)
            db.add(db_tenant)

            db.commit()
            db.refresh(db_tenant)
            db_tenant = db.query(TenantProfile).options(joinedload(TenantProfile.user)).filter(TenantProfile.id == db_tenant.id).first()

        except Exception as e:
            db.rollback()
            raise e

        return db_tenant


def get_tenants(db: Session, skip: int = 0, max_limit= 50):
    return db.query(TenantProfile).offset(skip).limit(max_limit).all()


def get_tenant(db: Session , tenant_id):
    return db.query(TenantProfile).filter(TenantProfile.id == tenant_id).first()

def get_tenant_by_email(db: Session, email: str):
    return db.query(TenantProfile).filter(TenantProfile.email == email).first()


crud_tenant = CRUDTenantProfile(TenantProfile)

def update_tenant(db: Session, db_tenant: TenantProfile, tenant_data: TenantProfileUpdate):


    # Only extract fields that were actually provided in the update request
    update_data = tenant_data.model_dump(exclude_unset=True)

    # Update the model attributes dynamically
    for key, value in update_data.items():
        setattr(db_tenant, key, value)

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def delete_tenant(db: Session, db_tenant: TenantProfile):
    db.delete(db_tenant)
    db.commit()

