import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contact_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "contact_user_id", name="unique_user_contact"),
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="contacts")
    contact_user = relationship("User", foreign_keys=[contact_user_id])
