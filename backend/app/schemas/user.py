from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    phone_number: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=6)

class VerifyOTPRequest(BaseModel):
    username: str
    phone_number: str
    password: str
    otp: str
    display_name: str
    avatar: Optional[str] = None

class UserLogin(BaseModel):
    username_or_phone: str
    password: str

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    display_name: str
    avatar: Optional[str] = None
    status: str
    is_online: bool
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
