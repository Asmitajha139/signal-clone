from typing import List, Optional
from pydantic import BaseModel, Field

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    member_ids: List[int] = Field(..., min_items=1)

class AddMemberRequest(BaseModel):
    user_id: int
