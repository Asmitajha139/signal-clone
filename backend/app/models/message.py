import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # "text", "system"
    status = Column(String, default="sent")        # "sending", "sent", "delivered", "read"
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    reads = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")
