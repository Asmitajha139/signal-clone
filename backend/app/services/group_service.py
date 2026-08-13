from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message
from app.models.user import User

class GroupService:
    @staticmethod
    def create_group(creator_id: int, name: str, member_ids: List[int], db: Session) -> Conversation:
        # Create group conversation
        conv = Conversation(type="group", name=name)
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # Add creator as admin
        creator_member = ConversationMember(conversation_id=conv.id, user_id=creator_id, role="admin")
        db.add(creator_member)

        # Add members
        all_member_ids = set(member_ids)
        if creator_id in all_member_ids:
            all_member_ids.remove(creator_id)

        for u_id in all_member_ids:
            user = db.query(User).filter(User.id == u_id).first()
            if user:
                mem = ConversationMember(conversation_id=conv.id, user_id=u_id, role="member")
                db.add(mem)

        # Add system message for group creation
        creator_user = db.query(User).filter(User.id == creator_id).first()
        sys_msg = Message(
            conversation_id=conv.id,
            sender_id=creator_id,
            content=f"{creator_user.display_name} created the group '{name}'",
            message_type="system",
            status="read"
        )
        db.add(sys_msg)

        db.commit()
        return conv

    @staticmethod
    def add_member(group_id: int, admin_user_id: int, target_user_id: int, db: Session):
        # Verify admin role
        admin_member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == group_id,
            ConversationMember.user_id == admin_user_id,
            ConversationMember.role == "admin"
        ).first()

        if not admin_member:
            raise HTTPException(status_code=403, detail="Only group admins can add members")

        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User to add not found")

        existing_member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == group_id,
            ConversationMember.user_id == target_user_id
        ).first()

        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a member of this group")

        new_member = ConversationMember(conversation_id=group_id, user_id=target_user_id, role="member")
        db.add(new_member)

        # Add system message
        admin_user = db.query(User).filter(User.id == admin_user_id).first()
        sys_msg = Message(
            conversation_id=group_id,
            sender_id=admin_user_id,
            content=f"{admin_user.display_name} added {target_user.display_name} to the group",
            message_type="system",
            status="read"
        )
        db.add(sys_msg)

        db.commit()
        return new_member

    @staticmethod
    def remove_member(group_id: int, admin_user_id: int, target_user_id: int, db: Session):
        # Verify admin role
        admin_member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == group_id,
            ConversationMember.user_id == admin_user_id,
            ConversationMember.role == "admin"
        ).first()

        if not admin_member:
            raise HTTPException(status_code=403, detail="Only group admins can remove members")

        target_member = db.query(ConversationMember).filter(
            ConversationMember.conversation_id == group_id,
            ConversationMember.user_id == target_user_id
        ).first()

        if not target_member:
            raise HTTPException(status_code=404, detail="Member not found in group")

        target_user = target_member.user
        admin_user = db.query(User).filter(User.id == admin_user_id).first()

        db.delete(target_member)

        # Add system message
        sys_msg = Message(
            conversation_id=group_id,
            sender_id=admin_user_id,
            content=f"{admin_user.display_name} removed {target_user.display_name} from the group",
            message_type="system",
            status="read"
        )
        db.add(sys_msg)

        db.commit()
        return {"message": f"Successfully removed {target_user.display_name} from group"}
