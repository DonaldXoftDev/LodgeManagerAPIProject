"""
TypedDict definitions for generic extra data.

This module contains definitions for generic dictionaries used to pass
around extra user information or context.
"""
from typing import TypedDict, Annotated
from pydantic import Field
from app.core.enums import UserRole

class GenericExtras(TypedDict):
    """
    A typed dictionary for generic extra user data.

    Attributes:
        role (UserRole): The user's role.
        landlord_id (int): The landlord's ID.
        lodge_id (int): The lodge's ID.
        hashed_password (str): The hashed password.
    """
    role: Annotated[UserRole, Field(..., description="The user's role.", examples=["LANDLORD"])]
    landlord_id: Annotated[int, Field(..., description="The landlord's ID.", examples=[1])]
    lodge_id: Annotated[int, Field(..., description="The lodge's ID.", examples=[1])]
    hashed_password: Annotated[str, Field(..., description="The hashed password.", examples=["$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"])]