from app.core.enums import TenantType
from app.db.session import  Base
from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship


class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String(50), nullable=False, unique=True, index=True)
    phone_no = Column(String(20), nullable=False, unique=True, index=True)
    tenant_type = Column(Enum(TenantType), nullable=False, default=TenantType.STUDENT)
    # leases = relationship('Lease', back_populates='tenant')

    def __repr__(self):
        return (f'<(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, phone_no={self.phone_no}'
                f' tenant_type={self.tenant_type})>')


