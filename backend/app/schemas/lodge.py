"""
Pydantic schemas for the lodge domain.

This module contains schemas used to represent, create, and update lodges.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.schemas.room import RoomResponse
from app.schemas.tenantprofile import TenantProfileResponse


class LodgeBase(BaseModel):
    """
    Base schema for a lodge.

    Attributes:
        name (str): The name of the lodge.
        address (str): The address of the lodge.
    """
    name: str
    address: str

    @field_validator('name', 'address')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()

class RoomGenerator(BaseModel):
    prefix: str = ""
    start_number: int
    end_number: int
    default_rent: int
    default_description: str

class LodgeCreate(LodgeBase):
    room_generator: Optional[RoomGenerator] = None

class LodgeInternal(LodgeBase):
    pass


class LodgeResponse(LodgeBase):
    id: int
    landlord_id: int
    created_at: datetime
    is_active: bool

    model_config = {'from_attributes': True}


class LodgeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

    @field_validator('name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.lower()
