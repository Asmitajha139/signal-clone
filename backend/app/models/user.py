import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    status = Column(String, default="Hey there! I am using Signal.")
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", foreign_keys="Contact.user_id", back_populates="user", cascade="all, delete-orphan")
    memberships = relationship("ConversationMember", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
