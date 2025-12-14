"""
Pydantic schemas for group-related requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.expense import ExpenseResponse


class GroupCreate(BaseModel):
    """Schema for group creation"""
    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    default_currency: str = Field(default="USD", min_length=3, max_length=3)
    simplify_debts: bool = Field(default=False)


class GroupUpdate(BaseModel):
    """Schema for group update"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    default_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    simplify_debts: Optional[bool] = None


class GroupResponse(BaseModel):
    """Schema for group response"""
    id: int
    public_id: str
    name: str
    user_id: int
    default_currency: str
    simplify_debts: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]

    class Config:
        from_attributes = True


class GroupMemberResponse(BaseModel):
    """Schema for group member"""
    user: UserResponse

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    """Schema for detailed group response with members and expenses"""
    members: List[UserResponse] = []
    recent_expenses: List[ExpenseResponse] = []

    class Config:
        from_attributes = True


class GroupBalanceResponse(BaseModel):
    """Schema for group balance"""
    user_id: int
    friend_id: int
    currency: str
    amount: int

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    """Schema for adding a member to a group"""
    group_id: int
    user_id: int


class RemoveMemberRequest(BaseModel):
    """Schema for removing a member from a group"""
    group_id: int
    user_id: int


class JoinGroupRequest(BaseModel):
    """Schema for joining a group by public ID"""
    public_id: str = Field(..., description="Public group ID")

