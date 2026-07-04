"""
Pydantic schemas for the user domain.

This module contains schemas used to represent, create, and update application users.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.core.enums import UserRole
#all users have email, password, phone no, first and last name
#landlords

class UserBase(BaseModel):
    """
    Base schema for a user.

    Attributes:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (EmailStr): The user's email address.
        phone_no (str): The user's phone number.
    """
    first_name: str = Field(..., description="The user's first name.", examples=["John"])
    last_name: str = Field(..., description="The user's last name.", examples=["Doe"])
    email: EmailStr = Field(..., description="The user's email address.", examples=["johndoe@example.com"])
    phone_no: str = Field(..., max_length=15, description="The user's phone number.", examples=["+2348012345678"])

    @field_validator('email', 'first_name', 'last_name', mode='before')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="The user's password.", examples=["strongpassword123"])

class UserInternal(UserBase):
    hashed_password: str = Field(..., description="The user's hashed password.", examples=["$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"])
    role: UserRole = Field(..., description="The user's role.", examples=["LANDLORD"])

class UserResponse(UserBase):
    id: int = Field(..., description="The unique identifier for the user.", examples=[1])
    is_active: bool = Field(..., description="Whether the user account is active.", examples=[True])
    created_at: datetime = Field(..., description="Timestamp when the user was created.", examples=["2026-07-04T06:05:02Z"])
    role: UserRole = Field(..., description="The user's role.", examples=["LANDLORD"])

    model_config = {'from_attributes': True}

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="The user's first name.", examples=["John"])
    last_name: Optional[str] = Field(None, description="The user's last name.", examples=["Doe"])
    phone_no: Optional[str] = Field(None, max_length=15, description="The user's phone number.", examples=["+2348012345678"])




class SecurityUserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="The user's email address.", examples=["johndoe@example.com"])
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="The user's new password.", examples=["newpassword123"])


class Token(BaseModel):
    access_token: str = Field(..., description="The access token.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    refresh_token: str = Field(..., description="The refresh token.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field('bearer', description="The type of the token.", examples=["bearer"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token to be used for generating a new access token.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])

