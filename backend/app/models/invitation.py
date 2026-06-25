
from app.core.enums import InviteStatus
from app.db.session import Base
from datetime import date, datetime
from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, Optional
import uuid

if TYPE_CHECKING:
    from app.models.lodge import Lodge


class Invite(Base):
    __tablename__ = 'invites'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    lodge_id: Mapped[int] = mapped_column(ForeignKey('lodges.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[InviteStatus] = mapped_column(default=InviteStatus.SENT, nullable=False)
    lodge: Mapped["Lodge"] = relationship(back_populates='invites')

    @property
    def lodge_name(self):
        return self.lodge.name if self.lodge else 'N/A'