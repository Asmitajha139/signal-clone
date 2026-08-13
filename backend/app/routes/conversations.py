from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationDetailResponse
from app.services.conversation_service import ConversationService
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("", response_model=List[ConversationResponse])
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService.get_user_conversations(current_user.id, db)

@router.post("", response_model=ConversationDetailResponse)
def create_direct_conversation(data: ConversationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = ConversationService.get_or_create_direct_conversation(current_user.id, data.user_id, db)
    return ConversationService.get_conversation_detail(conv.id, current_user.id, db)

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ConversationService.get_conversation_detail(conversation_id, current_user.id, db)
