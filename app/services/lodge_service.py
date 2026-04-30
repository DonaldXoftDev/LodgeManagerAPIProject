from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.schemas.lodge import LodgeCreate
from app.crud import lodge as crud_lodge
from app.services.exceptions import LodgeAlreadyExistError


def is_landlord(user_role: UserRole):
    return user_role == UserRole.LANDLORD


def create_lodge(db: Session, landlord_id: int, lodge_in: LodgeCreate):
    lodge_exist = crud_lodge.get_lodge_by_name_and_landlord(db, landlord_id=landlord_id, lodge_name=lodge_in.name)

    if lodge_exist:
        raise LodgeAlreadyExistError(f'Lodge with name: {lodge_in.name} already exists')

    return crud_lodge.create_lodge(db, lodge_data=lodge_in, landlord_id=landlord_id)