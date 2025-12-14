"""
Group router - handles group operations
Replaces tRPC groupRouter
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict
from datetime import datetime
from nanoid import generate as nanoid

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Group, GroupUser, Expense, BalanceView
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupDetailResponse,
    GroupBalanceResponse, AddMemberRequest, RemoveMemberRequest,
    JoinGroupRequest
)
from app.schemas.user import UserResponse
from app.schemas.expense import ExpenseResponse
from app.services.split_service import join_group, recalculate_group_balances

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupResponse)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new group

    Replaces tRPC: groupRouter.create
    """
    # Generate public ID for the group
    public_id = nanoid(size=10)

    group = Group(
        public_id=public_id,
        name=group_data.name,
        user_id=current_user.id,
        default_currency=group_data.default_currency,
        simplify_debts=group_data.simplify_debts,
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add creator as first member
    group_user = GroupUser(
        group_id=group.id,
        user_id=current_user.id
    )
    db.add(group_user)
    db.commit()

    return GroupResponse.model_validate(group)


@router.get("", response_model=List[GroupResponse])
async def get_all_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_archived: bool = Query(False, description="Include archived groups")
):
    """
    Get all groups for current user

    Replaces tRPC: groupRouter.getAllGroups
    """
    query = db.query(Group).join(GroupUser).filter(
        GroupUser.user_id == current_user.id
    )

    if not include_archived:
        query = query.filter(Group.archived_at.is_(None))

    groups = query.all()
    return [GroupResponse.model_validate(g) for g in groups]


@router.get("/with-balances", response_model=List[Dict])
async def get_groups_with_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_archived: Optional[bool] = Query(False, description="Include archived groups")
):
    """
    Get all groups with balance summaries

    Replaces tRPC: groupRouter.getAllGroupsWithBalances
    """
    query = db.query(Group).join(GroupUser).filter(
        GroupUser.user_id == current_user.id
    )

    if not include_archived:
        query = query.filter(Group.archived_at.is_(None))

    groups = query.all()

    result = []
    for group in groups:
        # Get balance summary for this group
        balances = db.query(BalanceView).filter(
            BalanceView.group_id == group.id,
            BalanceView.user_id == current_user.id
        ).all()

        balance_summary = {}
        for bal in balances:
            if bal.currency not in balance_summary:
                balance_summary[bal.currency] = 0
            balance_summary[bal.currency] += bal.amount

        result.append({
            "id": group.id,
            "name": group.name,
            "public_id": group.public_id,
            "default_currency": group.default_currency,
            "balances": balance_summary,
            "archived_at": group.archived_at.isoformat() if group.archived_at else None
        })

    return result


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group_details(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed group info with members and recent expenses

    Replaces tRPC: groupRouter.getGroupDetails
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if user is member
    is_member = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == current_user.id
        )
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Get members
    members = db.query(User).join(GroupUser).filter(
        GroupUser.group_id == group_id
    ).all()

    # Get recent expenses (last 50)
    expenses = db.query(Expense).filter(
        and_(
            Expense.group_id == group_id,
            Expense.deleted_at.is_(None)
        )
    ).order_by(Expense.expense_date.desc()).limit(50).all()

    response = GroupDetailResponse.model_validate(group)
    response.members = [UserResponse.model_validate(m) for m in members]
    response.recent_expenses = [ExpenseResponse.model_validate(e) for e in expenses]

    return response


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update group settings

    Replaces tRPC: groupRouter.updateGroupName
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Only creator can update
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can update settings"
        )

    if group_data.name is not None:
        group.name = group_data.name
    if group_data.default_currency is not None:
        group.default_currency = group_data.default_currency
    if group_data.simplify_debts is not None:
        group.simplify_debts = group_data.simplify_debts

    db.commit()
    db.refresh(group)

    return GroupResponse.model_validate(group)


@router.post("/join", response_model=GroupResponse)
async def join_group_by_public_id(
    request: JoinGroupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join a group using public ID

    Replaces tRPC: groupRouter.join (indirectly via splitService.joinGroup)
    """
    group = await join_group(db, current_user.id, request.public_id)
    return GroupResponse.model_validate(group)


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to a group

    Replaces tRPC: groupRouter.addMember
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if requester is member
    is_member = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == current_user.id
        )
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Check if user to add exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already a member
    existing = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )

    # Add member
    group_user = GroupUser(group_id=group_id, user_id=user_id)
    db.add(group_user)
    db.commit()

    return {"message": "Member added successfully"}


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a group

    Replaces tRPC: groupRouter.removeMember
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Only creator can remove members
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can remove members"
        )

    # Can't remove self if creator
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use leave endpoint to leave group"
        )

    # Remove member
    result = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        )
    ).delete()

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member"
        )

    db.commit()
    return None


@router.post("/{group_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leave a group

    Replaces tRPC: groupRouter.leave
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Can't leave if creator (must transfer ownership first)
    if group.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group creator cannot leave. Transfer ownership or delete group."
        )

    # Remove membership
    result = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == current_user.id
        )
    ).delete()

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a member of this group"
        )

    db.commit()
    return None


@router.post("/{group_id}/archive", response_model=GroupResponse)
async def archive_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive a group (soft delete)

    Replaces tRPC: groupRouter.archiveGroup
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Only creator can archive
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can archive"
        )

    from datetime import datetime
    group.archived_at = datetime.utcnow()
    db.commit()
    db.refresh(group)

    return GroupResponse.model_validate(group)


@router.post("/{group_id}/recalculate", status_code=status.HTTP_204_NO_CONTENT)
async def recalculate_balances(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate all balances for a group from scratch

    Replaces tRPC: groupRouter.recalculateBalances
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Only creator can recalculate
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can recalculate balances"
        )

    await recalculate_group_balances(db, group_id)
    return None


@router.get("/{group_id}/balances", response_model=List[GroupBalanceResponse])
async def get_group_balances(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all balances within a group

    Part of groupRouter.getAllGroupsWithBalances functionality
    """
    # Check if user is member
    is_member = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == current_user.id
        )
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    balances = db.query(BalanceView).filter(BalanceView.group_id == group_id).all()
    return [GroupBalanceResponse.model_validate(b) for b in balances]


@router.get("/{group_id}/totals", response_model=List[Dict])
async def get_group_totals(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get total expenses per currency in a group

    Replaces tRPC: groupRouter.getGroupTotals
    """
    from sqlalchemy import func

    # Check if user is member
    is_member = db.query(GroupUser).filter(
        and_(
            GroupUser.group_id == group_id,
            GroupUser.user_id == current_user.id
        )
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    totals = db.query(
        Expense.currency,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.group_id == group_id,
        Expense.deleted_at.is_(None)
    ).group_by(Expense.currency).all()

    return [
        {"currency": t.currency, "total": t.total}
        for t in totals
    ]


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a group (only if all balances are zero)

    Replaces tRPC: groupRouter.delete
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Only creator can delete
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group creator can delete"
        )

    # Check for non-zero balances
    balances = db.query(BalanceView).filter(
        BalanceView.group_id == group_id,
        BalanceView.amount != 0
    ).first()

    if balances:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group with outstanding balances"
        )

    # Delete group (cascades to members, expenses, etc.)
    db.delete(group)
    db.commit()

    return None


@router.get("/with-balances", response_model=List[Dict])
async def get_all_groups_with_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_archived: bool = Query(False)
):
    """
    Get all groups with balance summaries

    Replaces tRPC: groupRouter.getAllGroupsWithBalances
    """
    query = db.query(Group).join(GroupUser).filter(
        GroupUser.user_id == current_user.id
    )

    if not include_archived:
        query = query.filter(Group.archived_at.is_(None))

    groups = query.all()

    result = []
    for group in groups:
        # Get balance summary for this group
        balances = db.query(BalanceView).filter(
            BalanceView.group_id == group.id,
            BalanceView.user_id == current_user.id
        ).all()

        # Get latest expense for sorting
        latest_expense = db.query(Expense).filter(
            Expense.group_id == group.id
        ).order_by(Expense.created_at.desc()).first()

        balance_by_currency = {}
        for b in balances:
            balance_by_currency[b.currency] = balance_by_currency.get(b.currency, 0) + b.amount

        result.append({
            "id": group.id,
            "name": group.name,
            "public_id": group.public_id,
            "default_currency": group.default_currency,
            "simplify_debts": group.simplify_debts,
            "created_at": group.created_at,
            "archived_at": group.archived_at,
            "balances": balance_by_currency,
            "latest_expense_at": latest_expense.created_at if latest_expense else None
        })

    # Sort by latest expense
    result.sort(key=lambda x: x["latest_expense_at"] or datetime.min, reverse=True)

    return result


