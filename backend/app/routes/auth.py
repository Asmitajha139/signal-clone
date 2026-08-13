from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserRegister, VerifyOTPRequest, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.services.presence_service import PresenceService
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_check(data, db)

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return AuthService.verify_otp_and_create_user(data, db)

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(data, db)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PresenceService.set_online_status(current_user.id, False, db)
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
