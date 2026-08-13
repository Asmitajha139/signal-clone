import os

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "signal_super_secret_jwt_key_2026_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./signal.db")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")

settings = Settings()

