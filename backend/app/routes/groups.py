from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.group import GroupCreate, AddMemberRequest
from app.schemas.conversation import ConversationDetailResponse
from app.services.group_service import GroupService
from app.services.conversation_service import ConversationService
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/groups", tags=["groups"])

@router.post("", response_model=ConversationDetailResponse)
def create_group(data: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = GroupService.create_group(current_user.id, data.name, data.member_ids, db)
    return ConversationService.get_conversation_detail(conv.id, current_user.id, db)

@router.get("/{group_id}", response_model=ConversationDetailResponse)
def get_group(group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService.get_conversation_detail(group_id, current_user.id, db)

@router.post("/{group_id}/members")
def add_group_member(group_id: int, data: AddMemberRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    GroupService.add_member(group_id, current_user.id, data.user_id, db)
    return {"message": "Member added successfully"}

@router.delete("/{group_id}/members/{target_user_id}")
def remove_group_member(group_id: int, target_user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GroupService.remove_member(group_id, current_user.id, target_user_id, db)
