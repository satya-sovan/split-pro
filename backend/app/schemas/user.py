"""
Pydantic schemas for user-related requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: Optional[str] = None  # Optional for OAuth users
    name: Optional[str] = None
    currency: str = "INR"  # Default to INR


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: Optional[str]
    email: Optional[str]
    image: Optional[str]
    currency: str
    preferred_language: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user preferences"""
    name: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    preferred_language: Optional[str] = None
    image: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class MagicLinkRequest(BaseModel):
    """Schema for magic link email request"""
    email: EmailStr


class MagicLinkVerify(BaseModel):
    """Schema for magic link verification"""
    token: str


class FriendResponse(BaseModel):
    """Schema for friend (user with balance) response"""
    user: UserResponse
    total_balance: int  # Sum of all balances with this friend
    balances: List[dict]  # Balances per currency

    class Config:
        from_attributes = True


class InviteFriendRequest(BaseModel):
    """Schema for inviting a friend"""
    email: EmailStr
    send_invite_email: bool = True


class PushSubscriptionRequest(BaseModel):
    """Schema for push notification subscription"""
    subscription: str = Field(..., description="Push subscription JSON from browser")


