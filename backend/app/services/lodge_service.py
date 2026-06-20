"""
Module providing lodge-related business logic.

This module contains services for managing lodges.
"""
from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.crud.room import crud_room
from app.models.lodge import Lodge
from app.models.room import Room
from app.schemas.lodge import LodgeCreate, LodgeUpdate, LodgeResponse, LodgeInternal
from app.core.exceptions import LodgeAlreadyExistError, LodgeNotFoundError
from app.crud.lodge import crud_lodge
from app.schemas.room import RoomCreate
from app.services import room_service


def is_landlord(user_role: UserRole):
    """
    Check if a user role is landlord.

    Args:
        user_role (UserRole): The user role to check.

    Returns:
        bool: True if landlord, False otherwise.
    """
    return user_role == UserRole.LANDLORD

def is_tenant(user_role: UserRole):
    """
    Check if a user role is tenant.

    Args:
        user_role (UserRole): The user role to check.

    Returns:
        bool: True if tenant, False otherwise.
    """
    return user_role == UserRole.TENANT





def create_new_lodge_for_landlord(db: Session, landlord_id: int, lodge_in: LodgeCreate):
    """
    Create a new lodge for a specific landlord.

    Args:
        db (Session): The database session.
        landlord_id (int): The ID of the landlord.
        lodge_in (LodgeCreate): The data to create the lodge.

    Returns:
        LodgeResponse: The newly created lodge.
    """
    lodge_exist = crud_lodge.get_by_name_and_landlord(db, landlord_id=landlord_id, lodge_name=lodge_in.name)

    if lodge_exist:
        raise LodgeAlreadyExistError(name=lodge_in.name)

    lodge_dict = lodge_in.model_dump(exclude={'room_generator'})
    new_lodge = Lodge(**lodge_dict, landlord_id=landlord_id)

    room_gen = lodge_in.room_generator

    if room_gen:
        start_num = room_gen.start_number
        end_num = room_gen.end_number
        prefix = room_gen.prefix

        for i in range(start_num, end_num + 1):
            room_no = f'{prefix}-{i}'
            room_data = Room(
             room_no = room_no,
            base_rent_price = room_gen.default_rent,
            description = room_gen.default_description
            )
            new_lodge.rooms.append(room_data)

    return crud_lodge.insert_lodge_tree(db, db_lodge= new_lodge)



def verify_lodge_ownership(db: Session, lodge_id:int, landlord_id: int):
    """
    Verify if a landlord owns a specific lodge.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_id (int): The ID of the landlord.

    Returns:
        Lodge: The verified lodge.
    """
    lodge = crud_lodge.get(db, item_id=lodge_id)

    if not lodge:
        raise LodgeNotFoundError()

    owned_by_landlord = lodge.landlord_id == landlord_id

    if not owned_by_landlord:
        raise LodgeNotFoundError()

    return lodge


def update_landlord_lodge(db:Session, lodge_id: int, landlord_id: int, update_data: LodgeUpdate):
    """
    Update details of a lodge owned by a landlord.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_id (int): The ID of the landlord.
        update_data (LodgeUpdate): The data to update.

    Returns:
        Lodge: The updated lodge.
    """
    lodge = verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    return crud_lodge.update(db=db, update_data=update_data, db_obj=lodge)


def landlord_owns_room_lodge(room: Room, landlord_id: int):
    """
    Check if a landlord owns the lodge containing a specific room.

    Args:
        room (Room): The room object.
        landlord_id (int): The ID of the landlord.

    Returns:
        bool: True if the landlord owns the lodge, False otherwise.
    """
    return room.lodge.landlord_id == landlord_id

