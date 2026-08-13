from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import UserResponse

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender: UserResponse
    content: str
    message_type: str
    status: str  # "sending", "sent", "delivered", "read"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MarkReadRequest(BaseModel):
    message_ids: Optional[List[int]] = None
