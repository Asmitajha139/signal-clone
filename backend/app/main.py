import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db, SessionLocal
from app.models import User, ConversationMember, Message
from app.utils.auth import decode_access_token
from app.websocket.manager import manager
from app.services.presence_service import PresenceService
from app.services.message_service import MessageService

from app.routes import auth, users, contacts, conversations, messages, groups

# Initialize database tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signal_app")

app = FastAPI(
    title="Signal Clone API",
    description="Backend API and WebSocket real-time engine for Signal Clone application",
    version="1.0.0"
)

from app.config import settings

# Configure CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(groups.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "name": "Signal Clone API Server",
        "docs": "/docs"
    }

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...)
):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=4001, reason="Unauthorized JWT token")
        return

    try:
        user_id = int(payload["sub"])
    except ValueError:
        await websocket.close(code=4001, reason="Invalid user ID in token")
        return

    db: Session = SessionLocal()
    try:
        # Verify user membership in conversation
        member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).first()

        if not member:
            await websocket.close(code=4003, reason="Forbidden conversation membership")
            return

        # Update presence online
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_online = True
            db.commit()

        await manager.connect(websocket, conversation_id, user_id)

        # Notify room of user presence
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "presence",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_online": True
            },
            exclude_user_id=user_id
        )

        try:
            while True:
                data_text = await websocket.receive_text()
                try:
                    data = json.loads(data_text)
                except Exception:
                    continue

                event_type = data.get("type")

                if event_type == "typing":
                    # Broadcast typing state to conversation room
                    is_typing = data.get("is_typing", True)
                    await manager.broadcast_to_conversation(
                        conversation_id,
                        {
                            "type": "typing",
                            "conversation_id": conversation_id,
                            "user_id": user_id,
                            "display_name": user.display_name if user else f"User {user_id}",
                            "is_typing": is_typing
                        },
                        exclude_user_id=user_id
                    )

                elif event_type == "message":
                    content = data.get("content", "").strip()
                    if content:
                        msg = MessageService.create_message(conversation_id, user_id, content, "text", db)
                        msg_data = {
                            "type": "message",
                            "conversation_id": conversation_id,
                            "message": {
                                "id": msg.id,
                                "conversation_id": msg.conversation_id,
                                "sender_id": msg.sender_id,
                                "sender": {
                                    "id": user.id,
                                    "username": user.username,
                                    "phone_number": user.phone_number,
                                    "display_name": user.display_name,
                                    "avatar": user.avatar,
                                    "status": user.status,
                                    "is_online": user.is_online,
                                    "created_at": user.created_at.isoformat() if user.created_at else None
                                },
                                "content": msg.content,
                                "message_type": msg.message_type,
                                "status": msg.status,
                                "created_at": msg.created_at.isoformat(),
                                "updated_at": msg.updated_at.isoformat()
                            }
                        }
                        await manager.broadcast_to_conversation(conversation_id, msg_data)

                elif event_type == "read":
                    message_ids = data.get("message_ids", [])
                    read_ids = MessageService.mark_messages_as_read(conversation_id, user_id, message_ids, db)
                    if read_ids:
                        await manager.broadcast_to_conversation(
                            conversation_id,
                            {
                                "type": "read",
                                "conversation_id": conversation_id,
                                "user_id": user_id,
                                "message_ids": read_ids
                            },
                            exclude_user_id=user_id
                        )

        except WebSocketDisconnect:
            manager.disconnect(websocket, conversation_id, user_id)
            if not manager.is_user_online(user_id):
                user_obj = db.query(User).filter(User.id == user_id).first()
                if user_obj:
                    user_obj.is_online = False
                    user_obj.last_seen = PresenceService.set_online_status(user_id, False, db).last_seen

            await manager.broadcast_to_conversation(
                conversation_id,
                {
                    "type": "presence",
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "is_online": False
                }
            )

    finally:
        db.close()
