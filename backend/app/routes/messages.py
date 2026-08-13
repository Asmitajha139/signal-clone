from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.message import MessageCreate, MessageResponse, MarkReadRequest
from app.services.message_service import MessageService
from app.models.user import User
from app.utils.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter(tags=["messages"])

@router.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conversation_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return MessageService.get_messages(conversation_id, current_user.id, limit, offset, db)

@router.post("/api/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = MessageService.create_message(conversation_id, current_user.id, data.content, data.message_type, db)

    # Broadcast via WebSocket manager to conversation room
    msg_payload = {
        "type": "message",
        "conversation_id": conversation_id,
        "message": {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "sender": {
                "id": current_user.id,
                "username": current_user.username,
                "phone_number": current_user.phone_number,
                "display_name": current_user.display_name,
                "avatar": current_user.avatar,
                "status": current_user.status,
                "is_online": current_user.is_online,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            },
            "content": msg.content,
            "message_type": msg.message_type,
            "status": msg.status,
            "created_at": msg.created_at.isoformat(),
            "updated_at": msg.updated_at.isoformat()
        }
    }

    await manager.broadcast_to_conversation(conversation_id, msg_payload)
    return msg

@router.patch("/api/conversations/{conversation_id}/read")
async def mark_read(
    conversation_id: int,
    data: Optional[MarkReadRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    message_ids = data.message_ids if data else None
    read_ids = MessageService.mark_messages_as_read(conversation_id, current_user.id, message_ids, db)

    if read_ids:
        # Broadcast read receipt via WebSocket
        read_payload = {
            "type": "read",
            "conversation_id": conversation_id,
            "user_id": current_user.id,
            "message_ids": read_ids
        }
        await manager.broadcast_to_conversation(conversation_id, read_payload, exclude_user_id=current_user.id)

    return {"message": "Marked as read", "read_message_ids": read_ids}
