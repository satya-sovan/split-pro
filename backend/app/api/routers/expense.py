"""
Expense router - handles expense CRUD operations
Replaces tRPC expenseRouter
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from uuid import uuid4

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Expense, ExpenseParticipant, ExpenseRecurrence
from app.schemas.expense import (
    ExpenseCreate, ExpenseResponse, ExpenseDetailResponse,
    DeleteExpenseRequest, BalanceResponse, CurrencyConversionCreate,
    ParticipantResponse, RecurringExpenseResponse, UploadUrlResponse
)
from app.services.split_service import (
    create_expense, delete_expense, edit_expense, get_user_balances
)
from app.services.currency_service import currency_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


# ============================================
# SPECIFIC ROUTES FIRST (before /{expense_id})
# ============================================

@router.get("/balances/all", response_model=List[BalanceResponse])
async def get_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    currency: Optional[str] = Query(None, description="Filter by currency")
):
    """Get all balances for current user"""
    balances = await get_user_balances(db, current_user.id, currency)
    return [BalanceResponse.model_validate(b) for b in balances]


@router.get("/recurring")
async def get_recurring_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recurring expense schedules for current user"""
    recurrences = db.query(ExpenseRecurrence).join(Expense).join(ExpenseParticipant).filter(
        Expense.deleted_at.is_(None),
        ExpenseParticipant.user_id == current_user.id
    ).all()

    return [
        {
            "id": r.id,
            "expense_id": r.expense_id,
            "job_id": r.job_id,
            "schedule": r.schedule
        }
        for r in recurrences
    ]


@router.get("/currency-rate")
async def get_currency_rate(
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Get exchange rate between two currencies"""
    from datetime import datetime as dt

    try:
        rate_date = dt.fromisoformat(date_str).date() if date_str else dt.utcnow().date()
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    rate = await currency_service.get_rate(db, from_currency, to_currency, rate_date)
    return {"rate": rate, "from": from_currency, "to": to_currency, "date": str(rate_date)}


@router.post("/currency-rates/batch")
async def get_batch_currency_rates(
    from_currencies: List[str] = Query(..., description="List of source currency codes"),
    to_currency: str = Query(..., description="Target currency code"),
    date_str: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Get exchange rates for multiple currencies"""
    from datetime import datetime as dt

    try:
        rate_date = dt.fromisoformat(date_str).date() if date_str else dt.utcnow().date()
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    rates = await currency_service.get_batch_rates(db, from_currencies, to_currency, rate_date)
    return {"rates": rates, "to": to_currency, "date": str(rate_date)}


@router.post("/upload-url")
async def get_upload_url(
    file_name: str = Query(..., description="Original file name"),
    file_type: str = Query(..., description="MIME type"),
    file_size: int = Query(..., description="File size in bytes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a pre-signed URL for uploading expense receipts"""
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    file_extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
    unique_id = str(uuid4())
    key = f"{current_user.id}/{unique_id}.{file_extension}"

    upload_url = await storage_service.get_upload_url(key, file_type, file_size)

    return {"upload_url": upload_url, "key": key}


@router.post("/currency-conversion", response_model=ExpenseResponse)
async def add_currency_conversion(
    conversion_data: CurrencyConversionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a currency conversion expense pair"""
    expense = await create_expense(
        db,
        conversion_data.from_expense,
        current_user.id,
        conversion_from_params=conversion_data.to_expense
    )
    return ExpenseResponse.model_validate(expense)


@router.get("/group/{group_id}/details", response_model=List[ExpenseDetailResponse])
async def get_group_expense_details(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False)
):
    """Get all expenses for a group with details"""
    query = db.query(Expense).filter(Expense.group_id == group_id)

    if not include_deleted:
        query = query.filter(Expense.deleted_at.is_(None))

    query = query.order_by(Expense.expense_date.desc())
    expenses = query.all()

    # Collect all user IDs we need
    all_user_ids = set()
    for expense in expenses:
        all_user_ids.add(expense.paid_by)

    # Get all participants
    expense_ids = [e.id for e in expenses]
    all_participants = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id.in_(expense_ids)
    ).all() if expense_ids else []

    for p in all_participants:
        all_user_ids.add(p.user_id)

    # Fetch all users at once
    users = db.query(User).filter(User.id.in_(all_user_ids)).all() if all_user_ids else []
    user_map = {u.id: u.name or u.email or f"User {u.id}" for u in users}

    # Group participants by expense_id
    participants_by_expense = {}
    for p in all_participants:
        if p.expense_id not in participants_by_expense:
            participants_by_expense[p.expense_id] = []
        participants_by_expense[p.expense_id].append(p)

    result = []
    for expense in expenses:
        participants = participants_by_expense.get(expense.id, [])

        response = ExpenseDetailResponse.model_validate(expense)
        response.paid_by_name = user_map.get(expense.paid_by, "Unknown")
        response.participants = [
            ParticipantResponse(
                user_id=p.user_id,
                user_name=user_map.get(p.user_id, "Unknown"),
                amount=p.amount
            ) for p in participants
        ]
        result.append(response)

    return result


@router.get("/friend/{friend_id}", response_model=List[ExpenseDetailResponse])
async def get_expenses_with_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False)
):
    """Get all expenses between current user and a specific friend"""
    from sqlalchemy import and_, or_

    query = db.query(Expense).join(ExpenseParticipant).filter(
        and_(
            Expense.id.in_(
                db.query(ExpenseParticipant.expense_id).filter(
                    ExpenseParticipant.user_id == current_user.id,
                    ExpenseParticipant.amount != 0
                )
            ),
            Expense.id.in_(
                db.query(ExpenseParticipant.expense_id).filter(
                    ExpenseParticipant.user_id == friend_id,
                    ExpenseParticipant.amount != 0
                )
            ),
            or_(
                Expense.paid_by == current_user.id,
                Expense.paid_by == friend_id
            )
        )
    )

    if not include_deleted:
        query = query.filter(Expense.deleted_at.is_(None))

    query = query.order_by(Expense.expense_date.desc())
    expenses = query.all()

    # Get user names for current user and friend
    users = db.query(User).filter(User.id.in_([current_user.id, friend_id])).all()
    user_map = {u.id: u.name or u.email or f"User {u.id}" for u in users}

    result = []
    for expense in expenses:
        participants = db.query(ExpenseParticipant).filter(
            ExpenseParticipant.expense_id == expense.id,
            or_(
                ExpenseParticipant.user_id == current_user.id,
                ExpenseParticipant.user_id == friend_id
            )
        ).all()

        response = ExpenseDetailResponse.model_validate(expense)
        response.paid_by_name = user_map.get(expense.paid_by, "Unknown")
        response.participants = [
            ParticipantResponse(
                user_id=p.user_id,
                user_name=user_map.get(p.user_id, "Unknown"),
                amount=p.amount
            ) for p in participants
        ]
        result.append(response)

    return result


# ============================================
# ROOT AND PARAMETERIZED ROUTES LAST
# ============================================

@router.get("", response_model=List[ExpenseResponse])
async def get_all_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    group_id: Optional[int] = Query(None, description="Filter by group ID"),
    include_deleted: bool = Query(False, description="Include deleted expenses")
):
    """Get all expenses for current user"""
    query = db.query(Expense).join(ExpenseParticipant).filter(
        ExpenseParticipant.user_id == current_user.id
    )

    if group_id:
        query = query.filter(Expense.group_id == group_id)

    if not include_deleted:
        query = query.filter(Expense.deleted_at.is_(None))

    query = query.order_by(Expense.expense_date.desc())
    expenses = query.all()
    return [ExpenseResponse.model_validate(e) for e in expenses]


@router.post("", response_model=ExpenseResponse)
async def add_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    expense = await create_expense(db, expense_data, current_user.id)
    return ExpenseResponse.model_validate(expense)


@router.get("/{expense_id}", response_model=ExpenseDetailResponse)
async def get_expense(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expense details with participants"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Get payer name
    payer = db.query(User).filter(User.id == expense.paid_by).first()

    participants = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id == expense_id
    ).all()

    # Get user names for participants
    participant_ids = [p.user_id for p in participants]
    users = db.query(User).filter(User.id.in_(participant_ids)).all()
    user_map = {u.id: u.name or u.email or f"User {u.id}" for u in users}

    response = ExpenseDetailResponse.model_validate(expense)
    response.paid_by_name = payer.name or payer.email if payer else "Unknown"
    response.participants = [
        ParticipantResponse(
            user_id=p.user_id,
            user_name=user_map.get(p.user_id, "Unknown"),
            amount=p.amount
        ) for p in participants
    ]

    return response


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    expense_data.expense_id = expense_id
    expense = await edit_expense(db, expense_data, current_user.id)
    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_expense(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense (soft delete)"""
    await delete_expense(db, expense_id, current_user.id)
    return None


# ==========================================
# EXPENSE NOTES
# ==========================================

@router.get("/{expense_id}/notes")
async def get_expense_notes(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes for an expense
    """
    from app.models.models import ExpenseNote

    # Verify expense exists and user has access
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Check user has access (is participant or payer)
    participant = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id == expense_id,
        ExpenseParticipant.user_id == current_user.id
    ).first()

    if not participant and expense.paid_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this expense"
        )

    notes = db.query(ExpenseNote).filter(
        ExpenseNote.expense_id == expense_id
    ).order_by(ExpenseNote.created_at.desc()).all()

    # Get user info for note authors
    user_ids = list(set(n.created_by_id for n in notes))
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: {"name": u.name or u.email, "image": u.image} for u in users}

    return [
        {
            "id": n.id,
            "note": n.note,
            "created_by_id": n.created_by_id,
            "created_by_name": user_map.get(n.created_by_id, {}).get("name", "Unknown"),
            "created_by_image": user_map.get(n.created_by_id, {}).get("image"),
            "created_at": n.created_at.isoformat(),
            "expense_id": n.expense_id
        }
        for n in notes
    ]


@router.post("/{expense_id}/notes")
async def add_expense_note(
    expense_id: str,
    note: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a note to an expense
    """
    from app.models.models import ExpenseNote

    # Verify expense exists
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Check user has access (is participant or payer)
    participant = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id == expense_id,
        ExpenseParticipant.user_id == current_user.id
    ).first()

    if not participant and expense.paid_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this expense"
        )

    # Validate note
    if not note or len(note.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note cannot be empty"
        )

    if len(note) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note is too long (max 1000 characters)"
        )

    # Create note
    new_note = ExpenseNote(
        id=str(uuid4()),
        note=note.strip(),
        created_by_id=current_user.id,
        expense_id=expense_id
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return {
        "id": new_note.id,
        "note": new_note.note,
        "created_by_id": new_note.created_by_id,
        "created_by_name": current_user.name or current_user.email,
        "created_by_image": current_user.image,
        "created_at": new_note.created_at.isoformat(),
        "expense_id": new_note.expense_id
    }


@router.delete("/{expense_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_note(
    expense_id: str,
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a note from an expense (only the author can delete)
    """
    from app.models.models import ExpenseNote

    note = db.query(ExpenseNote).filter(
        ExpenseNote.id == note_id,
        ExpenseNote.expense_id == expense_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Only the author can delete
    if note.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own notes"
        )

    db.delete(note)
    db.commit()

    return None

