"""
Split service - Core business logic for expense splitting and balance calculations
Ported from src/server/api/services/splitService.ts
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import uuid

from app.models.models import (
    Expense, ExpenseParticipant, User, Group, GroupUser,
    BalanceView, SplitType, ExpenseRecurrence
)
from app.schemas.expense import ExpenseCreate, ParticipantCreate


def get_non_zero_participants(participants: List[ParticipantCreate]) -> List[Dict]:
    """Filter out participants with zero amounts"""
    return [
        {"user_id": p.user_id, "amount": p.amount}
        for p in participants
        if p.amount != 0
    ]


async def join_group(db: Session, user_id: int, public_group_id: str) -> Group:
    """Add a user to a group by public ID"""
    group = db.query(Group).filter(Group.public_id == public_group_id).first()

    if not group:
        raise ValueError("Group not found")

    # Check if user is already in group
    existing = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group.id,
            GroupUser.user_id == user_id
        )
    ).first()

    if not existing:
        group_user = GroupUser(group_id=group.id, user_id=user_id)
        db.add(group_user)
        db.commit()

    return group


async def create_expense(
    db: Session,
    expense_data: ExpenseCreate,
    current_user_id: int,
    conversion_from_params: Optional[ExpenseCreate] = None
) -> Expense:
    """
    Create a new expense with participants and update balances

    This is the core expense creation logic ported from TypeScript.
    All amounts are in BigInt (cents).
    """
    non_zero_participants = get_non_zero_participants(expense_data.participants)

    # Generate UUID for expense
    expense_id = str(uuid.uuid4())

    # Create main expense
    expense = Expense(
        id=expense_id,
        group_id=expense_data.group_id,
        paid_by=expense_data.paid_by,
        name=expense_data.name,
        category=expense_data.category,
        amount=expense_data.amount,
        split_type=expense_data.split_type,
        currency=expense_data.currency,
        file_key=expense_data.file_key,
        added_by=current_user_id,
        expense_date=expense_data.expense_date or datetime.utcnow(),
        transaction_id=expense_data.transaction_id,
    )
    db.add(expense)

    # Create participant records
    for participant_data in non_zero_participants:
        participant = ExpenseParticipant(
            expense_id=expense_id,
            user_id=participant_data["user_id"],
            amount=participant_data["amount"]
        )
        db.add(participant)

    # Update balances - the payer is owed by each participant
    payer_id = expense_data.paid_by
    for participant_data in non_zero_participants:
        participant_id = participant_data["user_id"]
        amount = participant_data["amount"]

        if participant_id == payer_id:
            continue  # Payer doesn't owe themselves

        # Update balance: payer is owed by participant (double-entry)
        await _update_balance(
            db, payer_id, participant_id, expense_data.group_id,
            expense_data.currency, amount
        )

    # Handle currency conversion expense if provided
    if conversion_from_params:
        conversion_expense_id = str(uuid.uuid4())
        conversion_participants = get_non_zero_participants(conversion_from_params.participants)

        conversion_expense = Expense(
            id=conversion_expense_id,
            group_id=conversion_from_params.group_id,
            paid_by=conversion_from_params.paid_by,
            name=conversion_from_params.name,
            category=conversion_from_params.category,
            amount=conversion_from_params.amount,
            split_type=conversion_from_params.split_type,
            currency=conversion_from_params.currency,
            file_key=conversion_from_params.file_key,
            added_by=current_user_id,
            expense_date=conversion_from_params.expense_date or datetime.utcnow(),
        )
        db.add(conversion_expense)

        # Link conversion expenses
        expense.conversion_to_id = conversion_expense_id

        # Create conversion participants
        for participant_data in conversion_participants:
            participant = ExpenseParticipant(
                expense_id=conversion_expense_id,
                user_id=participant_data["user_id"],
                amount=participant_data["amount"]
            )
            db.add(participant)

        # Update balances for conversion expense
        conversion_payer_id = conversion_from_params.paid_by
        for participant_data in conversion_participants:
            participant_id = participant_data["user_id"]
            amount = participant_data["amount"]

            if participant_id == conversion_payer_id:
                continue

            await _update_balance(
                db, conversion_payer_id, participant_id, conversion_from_params.group_id,
                conversion_from_params.currency, amount
            )

    db.commit()
    db.refresh(expense)

    # Send push notification (async, don't block)
    # await send_expense_push_notification(expense_id)

    return expense


async def _update_balance(
    db: Session,
    payer_id: int,
    participant_id: int,
    group_id: Optional[int],
    currency: str,
    amount: int
) -> None:
    """
    Update balance between payer and participant (double-entry bookkeeping)

    Payer's balance with participant: negative (participant owes payer)
    Participant's balance with payer: positive (they owe the payer)
    """
    # Update payer's view: participant owes them (negative in their balance_view)
    payer_balance = db.query(BalanceView).filter(
        and_(
            BalanceView.user_id == payer_id,
            BalanceView.friend_id == participant_id,
            BalanceView.group_id == group_id if group_id else BalanceView.group_id.is_(None),
            BalanceView.currency == currency
        )
    ).first()

    if payer_balance:
        payer_balance.amount -= amount  # Payer is owed (negative = they get money)
        payer_balance.updated_at = datetime.utcnow()
    else:
        payer_balance = BalanceView(
            user_id=payer_id,
            friend_id=participant_id,
            group_id=group_id,
            currency=currency,
            amount=-amount,  # Negative means they are owed
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(payer_balance)

    # Update participant's view: they owe payer (positive in their balance_view)
    participant_balance = db.query(BalanceView).filter(
        and_(
            BalanceView.user_id == participant_id,
            BalanceView.friend_id == payer_id,
            BalanceView.group_id == group_id if group_id else BalanceView.group_id.is_(None),
            BalanceView.currency == currency
        )
    ).first()

    if participant_balance:
        participant_balance.amount += amount  # Participant owes (positive = they owe money)
        participant_balance.updated_at = datetime.utcnow()
    else:
        participant_balance = BalanceView(
            user_id=participant_id,
            friend_id=payer_id,
            group_id=group_id,
            currency=currency,
            amount=amount,  # Positive means they owe
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(participant_balance)


async def delete_expense(
    db: Session,
    expense_id: str,
    deleted_by: int
) -> None:
    """
    Soft-delete an expense by setting deletedAt timestamp
    Also reverses the balance changes made by this expense.
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise ValueError("Expense not found")

    # If this expense has a currency conversion, delete that too
    if expense.conversion_to_id:
        await delete_expense(db, expense.conversion_to_id, deleted_by)

    # Reverse balance changes before deleting
    participants = db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id == expense_id
    ).all()

    payer_id = expense.paid_by
    for participant in participants:
        if participant.user_id == payer_id:
            continue

        # Reverse the balance: participant no longer owes payer
        await _update_balance(
            db, payer_id, participant.user_id, expense.group_id,
            expense.currency, -participant.amount  # Negative to reverse
        )

    # Soft delete the expense
    expense.deleted_at = datetime.utcnow()
    expense.deleted_by = deleted_by

    # Handle recurring expense cleanup
    if expense.recurrence_id:
        # Check if there are other expenses linked to this recurrence
        linked_count = db.query(Expense).filter(
            and_(
                Expense.recurrence_id == expense.recurrence_id,
                Expense.id != expense_id
            )
        ).count()

        # If this is the last expense, delete the recurrence job
        if linked_count == 0:
            recurrence = db.query(ExpenseRecurrence).filter(
                ExpenseRecurrence.id == expense.recurrence_id
            ).first()
            if recurrence:
                # TODO: Unschedule APScheduler job
                db.delete(recurrence)

    db.commit()

    # Send push notification
    # await send_expense_push_notification(expense_id)


async def edit_expense(
    db: Session,
    expense_data: ExpenseCreate,
    current_user_id: int,
    conversion_to_params: Optional[ExpenseCreate] = None
) -> Expense:
    """
    Edit an existing expense

    This deletes old participants and creates new ones, then updates the expense.
    """
    if not expense_data.expense_id:
        raise ValueError("Expense ID is required for editing")

    expense = db.query(Expense).filter(Expense.id == expense_data.expense_id).first()

    if not expense:
        raise ValueError("Expense not found")

    # Delete existing participants for this expense
    db.query(ExpenseParticipant).filter(
        ExpenseParticipant.expense_id == expense_data.expense_id
    ).delete()

    # If there's a conversion expense, delete its participants too
    if expense.conversion_to_id:
        db.query(ExpenseParticipant).filter(
            ExpenseParticipant.expense_id == expense.conversion_to_id
        ).delete()

    # Update expense fields
    expense.paid_by = expense_data.paid_by
    expense.name = expense_data.name
    expense.category = expense_data.category
    expense.amount = expense_data.amount
    expense.split_type = expense_data.split_type
    expense.currency = expense_data.currency
    expense.file_key = expense_data.file_key
    expense.transaction_id = expense_data.transaction_id
    expense.expense_date = expense_data.expense_date or expense.expense_date
    expense.updated_by = current_user_id
    expense.updated_at = datetime.utcnow()

    # Create new participants
    for participant_data in expense_data.participants:
        if participant_data.amount != 0:
            participant = ExpenseParticipant(
                expense_id=expense_data.expense_id,
                user_id=participant_data.user_id,
                amount=participant_data.amount
            )
            db.add(participant)

    # Handle conversion expense update
    if conversion_to_params and expense.conversion_to_id:
        conversion_expense = db.query(Expense).filter(
            Expense.id == expense.conversion_to_id
        ).first()

        if conversion_expense:
            conversion_expense.paid_by = conversion_to_params.paid_by
            conversion_expense.name = conversion_to_params.name
            conversion_expense.category = conversion_to_params.category
            conversion_expense.amount = conversion_to_params.amount
            conversion_expense.split_type = conversion_to_params.split_type
            conversion_expense.currency = conversion_to_params.currency
            conversion_expense.expense_date = conversion_to_params.expense_date or conversion_expense.expense_date
            conversion_expense.updated_by = current_user_id
            conversion_expense.updated_at = datetime.utcnow()

            # Create new participants for conversion
            for participant_data in conversion_to_params.participants:
                if participant_data.amount != 0:
                    participant = ExpenseParticipant(
                        expense_id=expense.conversion_to_id,
                        user_id=participant_data.user_id,
                        amount=participant_data.amount
                    )
                    db.add(participant)

    # Handle recurring expense cleanup
    if expense.recurrence_id:
        # TODO: Unschedule APScheduler job
        pass

    db.commit()
    db.refresh(expense)

    # Send push notification
    # await send_expense_push_notification(expense_data.expense_id)

    return expense


async def get_user_balances(
    db: Session,
    user_id: int,
    currency: Optional[str] = None
) -> List[BalanceView]:
    """
    Get all balances for a user

    The BalanceView is calculated from expenses automatically in MariaDB
    via triggers (replacing PostgreSQL materialized view).
    """
    query = db.query(BalanceView).filter(BalanceView.user_id == user_id)

    if currency:
        query = query.filter(BalanceView.currency == currency)

    balances = query.all()
    return balances


async def recalculate_group_balances(db: Session, group_id: int) -> None:
    """
    Recalculate all balances for a group from scratch

    This is used after imports or data repairs.
    In the new architecture, this would trigger a refresh of the BalanceView.
    """
    # In MariaDB, we would:
    # 1. Delete all balance_view records for this group
    # 2. Trigger recalculation from expenses

    # Delete existing balances for this group
    db.query(BalanceView).filter(BalanceView.group_id == group_id).delete()

    # Get all non-deleted expenses for this group
    expenses = db.query(Expense).filter(
        and_(
            Expense.group_id == group_id,
            Expense.deleted_at.is_(None)
        )
    ).all()

    # Recalculate balances from expenses
    balance_dict = {}

    for expense in expenses:
        participants = db.query(ExpenseParticipant).filter(
            ExpenseParticipant.expense_id == expense.id
        ).all()

        payer_id = expense.paid_by

        for participant in participants:
            if participant.user_id == payer_id:
                continue

            # Create balance key
            key = (payer_id, participant.user_id, group_id, expense.currency)
            reverse_key = (participant.user_id, payer_id, group_id, expense.currency)

            # Payer is owed (negative balance for participant)
            if key not in balance_dict:
                balance_dict[key] = 0
            balance_dict[key] -= participant.amount

            # Participant owes (positive balance)
            if reverse_key not in balance_dict:
                balance_dict[reverse_key] = 0
            balance_dict[reverse_key] += participant.amount

    # Insert recalculated balances
    for (user_id, friend_id, group_id, currency), amount in balance_dict.items():
        if amount != 0:  # Only store non-zero balances
            balance = BalanceView(
                user_id=user_id,
                friend_id=friend_id,
                group_id=group_id,
                currency=currency,
                amount=amount,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(balance)

    db.commit()

