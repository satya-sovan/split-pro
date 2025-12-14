"""
Pydantic schemas for bank transaction endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InstitutionResponse(BaseModel):
    """Schema for bank institution response"""
    institution_id: str
    name: str
    country: str
    logo: Optional[str] = None
    bic: Optional[str] = None


class ConnectBankRequest(BaseModel):
    """Schema for connecting to a bank"""
    institution_id: Optional[str] = None


class ConnectBankResponse(BaseModel):
    """Schema for bank connection response"""
    link_token: Optional[str] = None  # Plaid
    auth_link: Optional[str] = None  # GoCardless
    requisition_id: Optional[str] = None  # GoCardless


class ExchangeTokenRequest(BaseModel):
    """Schema for exchanging public token (Plaid)"""
    public_token: str = Field(..., description="Public token from Plaid Link")


class ExchangeTokenResponse(BaseModel):
    """Schema for token exchange response"""
    access_token: str
    item_id: str


class LinkTokenResponse(BaseModel):
    """Schema for Plaid Link token response"""
    link_token: str
    expiration: str


class TransactionResponse(BaseModel):
    """Schema for bank transaction response"""
    transaction_id: str
    account_id: Optional[str]
    amount: float
    currency: str
    date: str
    name: str
    merchant_name: Optional[str] = None
    category: List[str] = []
    pending: bool = False
    payment_channel: Optional[str] = None

    class Config:
        from_attributes = True


class ImportTransactionRequest(BaseModel):
    """Schema for importing transaction as expense"""
    transaction_id: str
    category: str
    participant_ids: Optional[List[int]] = None
    group_id: Optional[int] = None

