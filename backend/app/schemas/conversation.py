from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import UserResponse
from app.schemas.message import MessageResponse

class ConversationCreate(BaseModel):
    user_id: int  # For direct 1-to-1 conversation target user

class MemberResponse(BaseModel):
    id: int
    user_id: int
    user: UserResponse
    role: str  # "member" or "admin"
    joined_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    type: str  # "direct" or "group"
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    other_user: Optional[UserResponse] = None  # For direct conversations
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    members_count: int = 0

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    type: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    members: List[MemberResponse]
    other_user: Optional[UserResponse] = None

    class Config:
        from_attributes = True
