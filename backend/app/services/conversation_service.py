import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message
from app.models.message_read import MessageRead
from app.models.user import User

class ConversationService:
    @staticmethod
    def get_or_create_direct_conversation(user_id: int, target_user_id: int, db: Session) -> Conversation:
        if user_id == target_user_id:
            raise HTTPException(status_code=400, detail="Cannot create conversation with yourself")

        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=44, detail="Target user not found")

        # Find existing direct conversation between user_id and target_user_id
        user_conv_ids = [
            cm.conversation_id for cm in db.query(ConversationMember.conversation_id)
            .filter(ConversationMember.user_id == user_id).all()
        ]

        target_conv_ids = [
            cm.conversation_id for cm in db.query(ConversationMember.conversation_id)
            .filter(ConversationMember.user_id == target_user_id).all()
        ]

        common_ids = set(user_conv_ids).intersection(set(target_conv_ids))
        if common_ids:
            direct_conv = db.query(Conversation).filter(
                Conversation.id.in_(common_ids),
                Conversation.type == "direct"
            ).first()
            if direct_conv:
                return direct_conv

        # Create new direct conversation
        conv = Conversation(type="direct")
        db.add(conv)
        db.commit()
        db.refresh(conv)

        member1 = ConversationMember(conversation_id=conv.id, user_id=user_id, role="member")
        member2 = ConversationMember(conversation_id=conv.id, user_id=target_user_id, role="member")
        db.add_all([member1, member2])
        db.commit()

        return conv

    @staticmethod
    def get_user_conversations(user_id: int, db: Session) -> List[dict]:
        # Get all conversations for user
        memberships = db.query(ConversationMember).filter(ConversationMember.user_id == user_id).all()
        conv_ids = [m.conversation_id for m in memberships]

        if not conv_ids:
            return []

        conversations = db.query(Conversation).filter(Conversation.id.in_(conv_ids)).all()
        result = []

        for conv in conversations:
            # Find last message
            last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(desc(Message.created_at)).first()

            # Find unread count (messages sent by others in this conv not read by current user)
            unread_count = 0
            if last_msg:
                # Count messages in conv where sender_id != user_id and id not in MessageRead for user_id
                read_msg_ids = db.query(MessageRead.message_id).filter(MessageRead.user_id == user_id).subquery()
                unread_count = db.query(Message).filter(
                    Message.conversation_id == conv.id,
                    Message.sender_id != user_id,
                    ~Message.id.in_(read_msg_ids)
                ).count()

            # Get other user if direct conversation
            other_user = None
            if conv.type == "direct":
                other_member = db.query(ConversationMember).filter(
                    ConversationMember.conversation_id == conv.id,
                    ConversationMember.user_id != user_id
                ).first()
                if other_member:
                    other_user = other_member.user

            members_count = db.query(ConversationMember).filter(ConversationMember.conversation_id == conv.id).count()

            result.append({
                "id": conv.id,
                "type": conv.type,
                "name": conv.name,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "other_user": other_user,
                "last_message": last_msg,
                "unread_count": unread_count,
                "members_count": members_count
            })

        # Sort by last message created_at or conversation updated_at descending
        result.sort(key=lambda x: (x["last_message"].created_at if x["last_message"] else x["updated_at"]), reverse=True)
        return result

    @staticmethod
    def get_conversation_detail(conversation_id: int, user_id: int, db: Session):
        # Verify user is member of conversation
        member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).first()

        if not member:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")

        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        other_user = None
        if conv.type == "direct":
            other_member = db.query(ConversationMember).filter(
                ConversationMember.conversation_id == conv.id,
                ConversationMember.user_id != user_id
            ).first()
            if other_member:
                other_user = other_member.user

        return {
            "id": conv.id,
            "type": conv.type,
            "name": conv.name,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "members": conv.members,
            "other_user": other_user
        }
