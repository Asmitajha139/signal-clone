import datetime
from sqlalchemy.orm import Session
from app.models.user import User

class PresenceService:
    @staticmethod
    def set_online_status(user_id: int, is_online: bool, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_online = is_online
            if not is_online:
                user.last_seen = datetime.datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
