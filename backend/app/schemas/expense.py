"""
Pydantic schemas for expense-related requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.models import SplitType


class ParticipantCreate(BaseModel):
    """Schema for expense participant creation"""
    user_id: int = Field(..., description="User ID of participant")
    amount: int = Field(..., description="Amount in cents (BigInt)")

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v


class ExpenseCreate(BaseModel):
    """Schema for creating or editing an expense"""
    expense_id: Optional[str] = None  # Required for editing
    group_id: Optional[int] = None
    paid_by: int = Field(..., description="User ID who paid")
    name: str = Field(..., min_length=1, max_length=500, description="Expense name")
    category: str = Field(..., description="Expense category")
    amount: int = Field(..., description="Total amount in cents")
    split_type: SplitType = Field(default=SplitType.EQUAL, description="How to split")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code")
    participants: List[ParticipantCreate] = Field(..., description="List of participants with amounts")
    expense_date: Optional[datetime] = None
    file_key: Optional[str] = None
    transaction_id: Optional[str] = None
    recurrence_id: Optional[int] = None

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError('Currency must be 3-letter code')
        return v.upper()

    @field_validator('participants')
    def validate_participants(cls, v):
        if not v:
            raise ValueError('At least one participant required')
        return v


class ExpenseResponse(BaseModel):
    """Schema for expense response"""
    id: str
    group_id: Optional[int]
    paid_by: int
    paid_by_name: Optional[str] = None
    name: str
    category: str
    amount: int
    split_type: SplitType
    currency: str
    expense_date: datetime
    created_at: datetime
    updated_at: datetime
    file_key: Optional[str]
    deleted_at: Optional[datetime]
    conversion_to_id: Optional[str]

    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    """Schema for participant response"""
    user_id: int
    user_name: Optional[str] = None
    amount: int

    class Config:
        from_attributes = True


class ExpenseDetailResponse(ExpenseResponse):
    """Schema for detailed expense response with participants"""
    participants: List[ParticipantResponse] = []

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Schema for balance response"""
    user_id: int
    friend_id: int
    group_id: Optional[int]
    currency: str
    amount: int

    class Config:
        from_attributes = True


class CurrencyConversionCreate(BaseModel):
    """Schema for creating currency conversion"""
    from_expense: ExpenseCreate
    to_expense: ExpenseCreate


class DeleteExpenseRequest(BaseModel):
    """Schema for delete expense request"""
    expense_id: str


class RecurringExpenseResponse(BaseModel):
    """Schema for recurring expense response"""
    id: int
    expense_id: str
    job_id: Optional[str]
    schedule: Optional[str]  # Cron expression

    class Config:
        from_attributes = True


class UploadUrlResponse(BaseModel):
    """Schema for upload URL response"""
    upload_url: str = Field(..., description="Presigned URL for uploading")
    key: str = Field(..., description="S3 object key for the uploaded file")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeleteExpenseRequest(BaseModel):
    """Schema for deleting an expense"""
    expense_id: str = Field(..., description="Expense ID to delete")


class CurrencyConversionCreate(BaseModel):
    """Schema for currency conversion between two expenses"""
    from_expense: ExpenseCreate
    to_expense: ExpenseCreate

