"""
SQLAlchemy models for authentication tokens.
This module contains the database model for storing JWT refresh tokens to support persistent sessions.
"""
from sqlalchemy import ForeignKey

from app.db.session import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class RefreshToken(Base):
    """
    SQLAlchemy model representing a user's refresh token.
    
    Attributes:
        id: Primary key for the token record.
        user_id: Foreign key referencing the user who owns this token.
        token: The actual refresh token string.
    """
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token: Mapped[str] = mapped_column(nullable=False, unique=True)
    user: Mapped["User"] = relationship(back_populates='refresh_tokens')