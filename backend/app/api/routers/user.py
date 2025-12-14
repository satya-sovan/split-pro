"""
User router - handles user profile and preferences
Replaces tRPC userRouter
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Dict
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, BalanceView, Expense, Group, GroupUser, ExpenseParticipant, Account, Session
from app.schemas.user import (
    UserResponse, UserUpdate, FriendResponse,
    InviteFriendRequest, PushSubscriptionRequest
)
from app.services.push_service import push_service
from app.services.email_service import email_service
from app.services.splitwise_import_service import splitwise_import_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user info

    Replaces tRPC: userRouter.me
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user preferences

    Replaces tRPC: userRouter.updateCurrency, userRouter.updateLanguage
    """
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.currency is not None:
        current_user.currency = user_data.currency.upper()
    if user_data.preferred_language is not None:
        current_user.preferred_language = user_data.preferred_language
    if user_data.image is not None:
        current_user.image = user_data.image

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/friends", response_model=List[FriendResponse])
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all friends (users with balances) for current user

    Replaces tRPC: userRouter.getFriends
    """
    # Get all unique friend IDs from balances
    balances = db.query(BalanceView).filter(
        BalanceView.user_id == current_user.id
    ).all()

    friend_balances = {}

    for balance in balances:
        friend_id = balance.friend_id

        if friend_id not in friend_balances:
            friend_balances[friend_id] = {
                "total": 0,
                "by_currency": {}
            }

        friend_balances[friend_id]["total"] += balance.amount

        if balance.currency not in friend_balances[friend_id]["by_currency"]:
            friend_balances[friend_id]["by_currency"][balance.currency] = 0

        friend_balances[friend_id]["by_currency"][balance.currency] += balance.amount

    # Get friend user objects
    friend_ids = list(friend_balances.keys())
    friends = db.query(User).filter(User.id.in_(friend_ids)).all()

    result = []
    for friend in friends:
        balance_data = friend_balances[friend.id]
        result.append(FriendResponse(
            user=UserResponse.model_validate(friend),
            total_balance=balance_data["total"],
            balances=[
                {"currency": curr, "amount": amt}
                for curr, amt in balance_data["by_currency"].items()
            ]
        ))

    return result


@router.get("/search/email", response_model=UserResponse)
async def search_user_by_email(
    email: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for a user by email address
    Returns the user if found, 404 if not
    """
    # Case-insensitive search
    user = db.query(User).filter(
        User.email.ilike(email.strip())
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a friend"
        )

    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get public user details

    Replaces tRPC: userRouter.getUserDetails
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.post("/hide-friend/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def hide_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hide a friend from the friends list

    Updates hidden_friend_ids array
    """
    if not isinstance(current_user.hidden_friend_ids, list):
        current_user.hidden_friend_ids = []

    if friend_id not in current_user.hidden_friend_ids:
        current_user.hidden_friend_ids.append(friend_id)
        db.commit()

    return None


@router.post("/unhide-friend/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unhide_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unhide a friend from the friends list
    """
    if not isinstance(current_user.hidden_friend_ids, list):
        current_user.hidden_friend_ids = []

    if friend_id in current_user.hidden_friend_ids:
        current_user.hidden_friend_ids.remove(friend_id)
        db.commit()

    return None


@router.get("/data/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data as JSON

    Replaces tRPC: userRouter.downloadData
    """
    from sqlalchemy import and_, or_

    # Get all expenses where user is participant
    expenses = db.query(Expense).join(ExpenseParticipant).filter(
        ExpenseParticipant.user_id == current_user.id,
        Expense.deleted_at.is_(None)
    ).all()

    # Get all groups
    groups = db.query(Group).join(GroupUser).filter(
        GroupUser.user_id == current_user.id
    ).all()

    # Get all balances
    balances = db.query(BalanceView).filter(
        BalanceView.user_id == current_user.id
    ).all()

    # Compile data
    export_data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "currency": current_user.currency,
            "preferred_language": current_user.preferred_language,
            "created_at": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
        },
        "expenses": [
            {
                "id": e.id,
                "name": e.name,
                "amount": e.amount,
                "currency": e.currency,
                "category": e.category,
                "paid_by": e.paid_by,
                "group_id": e.group_id,
                "expense_date": e.expense_date.isoformat(),
                "created_at": e.created_at.isoformat()
            }
            for e in expenses
        ],
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "default_currency": g.default_currency,
                "created_at": g.created_at.isoformat() if hasattr(g, 'created_at') else None
            }
            for g in groups
        ],
        "balances": [
            {
                "friend_id": b.friend_id,
                "currency": b.currency,
                "amount": b.amount,
                "group_id": b.group_id
            }
            for b in balances
        ],
        "export_date": datetime.utcnow().isoformat(),
        "format_version": "1.0"
    }

    return export_data


@router.post("/import/splitwise", status_code=status.HTTP_200_OK)
async def import_from_splitwise(
    file: UploadFile = File(..., description="Splitwise CSV export file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import expenses from Splitwise CSV export

    Accepts a CSV file exported from Splitwise with columns:
    Date, Description, Category, Cost, Currency, [User1], [User2], ...

    Replaces tRPC: userRouter.importUsersFromSplitWise
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please upload a CSV file"
            )

        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')

        stats = await splitwise_import_service.import_from_csv(
            db=db,
            user_id=current_user.id,
            csv_content=csv_content
        )

        return {
            "success": True,
            "message": "Import completed",
            "statistics": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/expenses/own", response_model=List[Dict])
async def get_own_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get expenses paid by current user

    Replaces tRPC: userRouter.getOwnExpenses
    """
    expenses = db.query(Expense).filter(
        Expense.paid_by == current_user.id,
        Expense.deleted_at.is_(None)
    ).order_by(Expense.expense_date.desc()).all()

    return [
        {
            "id": e.id,
            "name": e.name,
            "amount": e.amount,
            "currency": e.currency,
            "category": e.category,
            "expense_date": e.expense_date.isoformat(),
            "group_id": e.group_id
        }
        for e in expenses
    ]


@router.post("/invite", response_model=UserResponse)
async def invite_friend(
    request: InviteFriendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a friend by email

    Replaces tRPC: userRouter.inviteFriend
    """
    # Check if user already exists
    friend = db.query(User).filter(User.email == request.email).first()

    if friend:
        return UserResponse.model_validate(friend)

    # Create new user
    new_user = User(
        email=request.email,
        name=request.email.split('@')[0],
        currency="USD",
        preferred_language="en"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send invite email if requested
    if request.send_invite_email:
        await email_service.send_invite_email(
            to_email=request.email,
            from_name=current_user.name or current_user.email
        )

    return UserResponse.model_validate(new_user)


@router.get("/balances/friend/{friend_id}", response_model=List[Dict])
async def get_balances_with_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get balance breakdown with a specific friend

    Replaces tRPC: userRouter.getBalancesWithFriend
    """
    balances = db.query(BalanceView).filter(
        BalanceView.user_id == current_user.id,
        BalanceView.friend_id == friend_id,
        BalanceView.amount != 0
    ).all()

    return [
        {
            "currency": b.currency,
            "amount": b.amount,
            "friend_id": friend_id
        }
        for b in balances
    ]


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    feedback: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit user feedback

    Replaces tRPC: userRouter.submitFeedback
    """
    if len(feedback) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback must be at least 10 characters"
        )

    await email_service.send_feedback_email(
        feedback=feedback,
        user=current_user
    )

    return None


@router.post("/push-subscription", status_code=status.HTTP_204_NO_CONTENT)
async def update_push_subscription(
    request: PushSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register push notification subscription

    Replaces tRPC: userRouter.updatePushNotification
    """
    await push_service.register_subscription(
        db,
        current_user.id,
        request.subscription
    )

    return None


@router.get("/push-public-key", response_model=Dict[str, str])
async def get_web_push_public_key(
    current_user: User = Depends(get_current_user)
):
    """
    Get VAPID public key for push notification setup

    Replaces tRPC: userRouter.getWebPushPublicKey
    """
    public_key = push_service.get_public_key()
    return {"publicKey": public_key}


# ==========================================
# PROFILE PICTURE UPLOAD
# ==========================================

@router.post("/profile-picture/upload-url", response_model=Dict[str, str])
async def get_profile_picture_upload_url(
    content_type: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
):
    """
    Get a presigned URL for uploading profile picture

    Returns a presigned URL that can be used to upload the image directly to S3/R2
    """
    from app.services.storage_service import storage_service
    import uuid

    # Validate content type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type. Allowed: {', '.join(allowed_types)}"
        )

    # Generate unique key for the profile picture
    extension = content_type.split('/')[-1]
    key = f"profile-pictures/{current_user.id}/{uuid.uuid4()}.{extension}"

    try:
        upload_url = await storage_service.get_upload_url(
            key=key,
            content_type=content_type,
            file_size=5 * 1024 * 1024,  # 5MB max
            expires_in=300  # 5 minutes
        )

        return {
            "upload_url": upload_url,
            "key": key
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service not configured"
        )


@router.post("/profile-picture", response_model=UserResponse)
async def update_profile_picture(
    key: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's profile picture URL after upload

    Called after successfully uploading to the presigned URL
    """
    from app.services.storage_service import storage_service

    # Delete old profile picture if it exists and is stored in our bucket
    if current_user.image and current_user.image.startswith('profile-pictures/'):
        await storage_service.delete_file(current_user.image)

    # Update user with new image key
    current_user.image = key
    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.delete("/profile-picture", response_model=UserResponse)
async def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user's profile picture
    """
    from app.services.storage_service import storage_service

    if current_user.image and current_user.image.startswith('profile-pictures/'):
        await storage_service.delete_file(current_user.image)

    current_user.image = None
    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/profile-picture-url", response_model=Dict[str, str])
async def get_profile_picture_url(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile picture URL (presigned for download)
    """
    from app.services.storage_service import storage_service

    if not current_user.image:
        return {"url": ""}

    # If it's already a full URL (from OAuth), return as-is
    if current_user.image.startswith('http'):
        return {"url": current_user.image}

    # Generate presigned URL for our stored images
    try:
        url = await storage_service.get_download_url(
            key=current_user.image,
            expires_in=3600  # 1 hour
        )
        return {"url": url}
    except Exception:
        return {"url": ""}


# ==========================================
# PASSWORD MANAGEMENT
# ==========================================

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user's password (for non-OAuth users)
    """
    from app.core.security import verify_password, get_password_hash

    # Check if user has a password (non-OAuth user)
    account = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.provider == "credentials"
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change not available for OAuth accounts"
        )

    # Verify current password
    if not account.access_token or not verify_password(current_password, account.access_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )

    # Update password
    account.access_token = get_password_hash(new_password)
    db.commit()

    return None


# ==========================================
# NOTIFICATION PREFERENCES
# ==========================================

@router.get("/notification-preferences", response_model=Dict)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's notification preferences
    """
    # Get or create preferences from user record
    # For now, use JSON field on user or return defaults
    prefs = getattr(current_user, 'notification_preferences', None)
    if not prefs:
        prefs = {
            "email_expense_added": True,
            "email_expense_updated": True,
            "email_payment_received": True,
            "email_weekly_summary": False,
            "push_expense_added": True,
            "push_expense_updated": True,
            "push_payment_received": True,
            "push_reminders": True
        }
    return prefs


@router.put("/notification-preferences", response_model=Dict)
async def update_notification_preferences(
    preferences: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's notification preferences
    """
    valid_keys = {
        "email_expense_added", "email_expense_updated", "email_payment_received",
        "email_weekly_summary", "push_expense_added", "push_expense_updated",
        "push_payment_received", "push_reminders"
    }

    # Validate keys
    for key in preferences:
        if key not in valid_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid preference key: {key}"
            )
        if not isinstance(preferences[key], bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Preference values must be boolean"
            )

    # Store preferences (this would need a notification_preferences JSON column on User)
    # For now, we'll simulate storage
    current_user.notification_preferences = preferences
    db.commit()

    return preferences


# ==========================================
# ACCOUNT DELETION
# ==========================================

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    password: str = Body(None, embed=True),
    confirmation: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete user account and all associated data

    Requires confirmation text "DELETE MY ACCOUNT" and password for non-OAuth users
    """
    from app.core.security import verify_password

    # Verify confirmation
    if confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please type 'DELETE MY ACCOUNT' to confirm"
        )

    # For non-OAuth users, verify password
    account = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.provider == "credentials"
    ).first()

    if account and account.access_token:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password required to delete account"
            )
        if not verify_password(password, account.access_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

    # Delete profile picture from storage
    from app.services.storage_service import storage_service
    if current_user.image and current_user.image.startswith('profile-pictures/'):
        await storage_service.delete_file(current_user.image)

    # Delete all user data (cascading deletes handle most relationships)
    # But we need to handle expenses carefully

    # Soft-delete expenses where user is payer
    expenses = db.query(Expense).filter(
        Expense.paid_by == current_user.id,
        Expense.deleted_at.is_(None)
    ).all()

    for expense in expenses:
        expense.deleted_at = datetime.utcnow()
        expense.deleted_by = current_user.id

    # Remove user from expense participants
    db.query(ExpenseParticipant).filter(
        ExpenseParticipant.user_id == current_user.id
    ).delete()

    # Remove from groups
    db.query(GroupUser).filter(
        GroupUser.user_id == current_user.id
    ).delete()

    # Delete sessions and accounts
    db.query(Session).filter(Session.user_id == current_user.id).delete()
    db.query(Account).filter(Account.user_id == current_user.id).delete()

    # Finally delete the user
    db.delete(current_user)
    db.commit()

    return None


