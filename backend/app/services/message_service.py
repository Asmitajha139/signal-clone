import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message
from app.models.message_read import MessageRead

class MessageService:
    @staticmethod
    def create_message(conversation_id: int, sender_id: int, content: str, message_type: str = "text", db: Session = None) -> Message:
        # Verify sender is member of conversation
        member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == sender_id
        ).first()

        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to send messages in this conversation")

        # Determine initial delivery status: if other members are online/connected, set status to delivered/sent
        msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            status="sent"
        )
        db.add(msg)

        # Update conversation updated_at
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            conv.updated_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_messages(conversation_id: int, user_id: int, limit: int = 100, offset: int = 0, db: Session = None) -> List[Message]:
        # Verify membership
        member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).first()

        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to view messages in this conversation")

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(offset).limit(limit).all()

        return messages

    @staticmethod
    def mark_messages_as_read(conversation_id: int, user_id: int, message_ids: Optional[List[int]], db: Session) -> List[int]:
        # Verify membership
        member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).first()

        if not member:
            raise HTTPException(status_code=403, detail="Not authorized")

        query = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id
        )

        if message_ids:
            query = query.filter(Message.id.in_(message_ids))

        messages_to_read = query.all()
        read_ids = []

        for msg in messages_to_read:
            # Check if entry already exists in MessageRead
            existing = db.query(MessageRead).filter(
                MessageRead.message_id == msg.id,
                MessageRead.user_id == user_id
            ).first()

            if not existing:
                read_entry = MessageRead(message_id=msg.id, user_id=user_id)
                db.add(read_entry)
                read_ids.append(msg.id)

            # Update status to read if direct or all members read
            msg.status = "read"

        db.commit()
        return read_ids
