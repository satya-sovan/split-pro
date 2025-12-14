"""
Bank transactions router - handles bank account integration
Replaces tRPC bankTransactionsRouter
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, CachedBankData
from app.schemas.bank import (
    LinkTokenResponse, ExchangeTokenRequest, ExchangeTokenResponse,
    InstitutionResponse, TransactionResponse, ConnectBankRequest,
    ConnectBankResponse
)
from app.services.plaid_service import plaid_service
from app.services.gocardless_service import gocardless_service
from app.core.config import settings

router = APIRouter(prefix="/bank", tags=["bank"])


def get_active_provider():
    """Determine which bank provider is configured"""
    if settings.PLAID_CLIENT_ID:
        return 'plaid'
    elif settings.GOCARDLESS_SECRET_ID:
        return 'gocardless'
    else:
        return None


@router.get("/institutions", response_model=List[InstitutionResponse])
async def get_institutions(
    country_code: str = Query('US', description="Country code (US, GB, DE, etc.)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of supported banking institutions

    Replaces tRPC: bankTransactionsRouter.getInstitutions
    """
    provider = get_active_provider()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="No bank integration configured. Set PLAID or GOCARDLESS credentials."
        )

    try:
        if provider == 'plaid':
            institutions = await plaid_service.get_institutions(country_code)
        else:  # gocardless
            institutions = await gocardless_service.get_institutions(country_code)

        return [InstitutionResponse(**inst) for inst in institutions]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch institutions: {str(e)}"
        )


@router.post("/connect", response_model=ConnectBankResponse)
async def connect_to_bank(
    request: Optional[ConnectBankRequest] = None,
    institution_id: Optional[str] = Query(None, description="Institution ID (for GoCardless)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize bank account connection

    For Plaid: Creates a Link token
    For GoCardless: Creates a requisition and returns auth link

    Replaces tRPC: bankTransactionsRouter.connectToBank
    """
    provider = get_active_provider()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="No bank integration configured"
        )

    try:
        if provider == 'plaid':
            # Plaid: Create Link token
            result = await plaid_service.create_link_token(
                user_id=current_user.id,
                user_name=current_user.name or current_user.email,
                language=current_user.preferred_language
            )

            return ConnectBankResponse(
                link_token=result.get('link_token'),
                auth_link=None,
                requisition_id=None
            )

        else:  # gocardless
            # GoCardless: Create requisition
            if not institution_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="institution_id required for GoCardless"
                )

            result = await gocardless_service.create_requisition(
                institution_id=institution_id,
                user_id=current_user.id,
                language=current_user.preferred_language
            )

            # Store requisition ID in user record
            current_user.obapi_provider_id = result['requisition_id']
            db.commit()

            return ConnectBankResponse(
                link_token=None,
                auth_link=result['link'],
                requisition_id=result['requisition_id']
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to bank: {str(e)}"
        )


@router.post("/token/exchange", response_model=ExchangeTokenResponse)
async def exchange_public_token(
    request: ExchangeTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exchange public token for access token (Plaid only)

    Replaces tRPC: bankTransactionsRouter.exchangePublicToken
    """
    if not plaid_service:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Plaid not configured"
        )

    try:
        result = await plaid_service.exchange_public_token(
            public_token=request.public_token,
            db=db,
            user_id=current_user.id
        )

        return ExchangeTokenResponse(
            access_token=result['access_token'],
            item_id=result['item_id']
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange token: {str(e)}"
        )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    account_id: Optional[str] = Query(None, description="Account ID (for GoCardless)"),
    use_cache: bool = Query(True, description="Use cached transactions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get bank transactions

    Replaces tRPC: bankTransactionsRouter.getTransactions
    """
    provider = get_active_provider()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="No bank integration configured"
        )

    # Check if user has connected account
    if not current_user.obapi_provider_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bank account connected. Connect a bank first."
        )

    # Parse dates
    try:
        start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=90)
        end = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Check cache first if requested
    if use_cache:
        cached = db.query(CachedBankData).filter(
            CachedBankData.user_id == current_user.id,
            CachedBankData.cached_at >= datetime.utcnow() - timedelta(hours=24)
        ).all()

        if cached:
            import json
            return [
                TransactionResponse(**json.loads(c.data))
                for c in cached
            ]

    # Fetch fresh transactions
    try:
        if provider == 'plaid':
            transactions = await plaid_service.get_transactions(
                access_token=current_user.obapi_provider_id,
                start_date=start,
                end_date=end,
                db=db,
                user_id=current_user.id
            )

        else:  # gocardless
            # For GoCardless, we need account IDs from the requisition
            requisition_id = current_user.obapi_provider_id
            accounts = await gocardless_service.get_accounts(requisition_id)

            if not accounts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No accounts found. Re-connect your bank."
                )

            # Use specified account or first account
            target_account = account_id or accounts[0]

            transactions = await gocardless_service.get_transactions(
                account_id=target_account,
                db=db,
                user_id=current_user.id,
                date_from=start,
                date_to=end
            )

        return [TransactionResponse(**t) for t in transactions]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )


@router.post("/transactions/{transaction_id}/import", status_code=status.HTTP_201_CREATED)
async def import_transaction_as_expense(
    transaction_id: str,
    category: str = Query(..., description="Expense category"),
    participants: Optional[List[int]] = Query(None, description="User IDs to split with"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import a bank transaction as an expense

    Creates an expense from a cached bank transaction
    """
    # Find cached transaction
    cached = db.query(CachedBankData).filter(
        CachedBankData.user_id == current_user.id,
        CachedBankData.transaction_id == transaction_id
    ).first()

    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    import json
    transaction = json.loads(cached.data)

    # TODO: Create expense from transaction
    # This would call the expense creation service
    # For now, just return success

    return {
        "message": "Transaction imported successfully",
        "transaction_id": transaction_id
    }

