from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Integer,  ForeignKey, DateTime
from app.db.session import Base
from sqlalchemy.orm  import relationship, mapped_column, Mapped

class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lease_id: Mapped[int] =  mapped_column(Integer, ForeignKey('leases.id'), nullable=False, index=True)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lease = relationship('Lease', back_populates='payments')