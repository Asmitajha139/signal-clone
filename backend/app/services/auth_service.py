from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserRegister, VerifyOTPRequest, UserLogin
from app.utils.security import hash_password, verify_password
from app.utils.auth import create_access_token

MOCK_OTP = "123456"

class AuthService:
    @staticmethod
    def register_check(data: UserRegister, db: Session):
        # Check if username or phone already exists
        existing_username = db.query(User).filter(User.username == data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username is already registered")

        existing_phone = db.query(User).filter(User.phone_number == data.phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number is already registered")

        return {"message": "OTP sent successfully", "mock_otp": MOCK_OTP}

    @staticmethod
    def verify_otp_and_create_user(data: VerifyOTPRequest, db: Session):
        if data.otp != MOCK_OTP:
            raise HTTPException(status_code=400, detail="Invalid OTP code. Use 123456 for testing.")

        # Re-check uniqueness
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=400, detail="Username is already registered")
        if db.query(User).filter(User.phone_number == data.phone_number).first():
            raise HTTPException(status_code=400, detail="Phone number is already registered")

        hashed_pwd = hash_password(data.password)
        new_user = User(
            username=data.username,
            phone_number=data.phone_number,
            password_hash=hashed_pwd,
            display_name=data.display_name,
            avatar=data.avatar,
            status="Hey there! I am using Signal.",
            is_online=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(data={"sub": str(new_user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user
        }

    @staticmethod
    def login(data: UserLogin, db: Session):
        user = db.query(User).filter(
            (User.username == data.username_or_phone) | (User.phone_number == data.username_or_phone)
        ).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username/phone or password")

        user.is_online = True
        db.commit()
        db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
