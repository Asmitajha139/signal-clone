from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse

class ContactCreate(BaseModel):
    contact_username_or_phone: str

class ContactResponse(BaseModel):
    id: int
    user_id: int
    contact_user_id: int
    contact_user: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True
