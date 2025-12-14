"""
Authentication router - handles login, registration, OAuth, magic links
Replaces NextAuth.js functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from datetime import timedelta
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, create_magic_link_token, verify_magic_link_token
)
from app.core.config import settings
from app.models.models import User, Account
from app.schemas.user import (
    UserCreate, UserLogin, TokenResponse, UserResponse,
    MagicLinkRequest, MagicLinkVerify
)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth configuration
oauth = OAuth()

if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password) if user_data.password else None
    user = User(
        email=user_data.email,
        name=user_data.name or user_data.email.split('@')[0],
        currency=user_data.currency or "INR",
        preferred_language="en",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create account record for email/password provider
    if hashed_password:
        account = Account(
            id=f"email_{user.id}",
            user_id=user.id,
            type="email",
            provider="email",
            provider_account_id=user_data.email,
            id_token=hashed_password,  # Store hashed password here
        )
        db.add(account)
        db.commit()

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Find email account
    account = db.query(Account).filter(
        Account.user_id == user.id,
        Account.provider == "email"
    ).first()

    if not account or not account.id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(login_data.password, account.id_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/magic-link", status_code=status.HTTP_200_OK)
async def send_magic_link(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """
    Send a magic link for passwordless login
    """
    # Check if user exists, create if not
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(
            email=request.email,
            name=request.email.split('@')[0],
            currency="USD",
            preferred_language="en",
        )
        db.add(user)
        db.commit()

    # Create magic link token
    token = create_magic_link_token(request.email)
    link = f"{settings.CORS_ORIGINS[0]}/auth/verify?token={token}"

    # TODO: Send email with link
    # await send_email(
    #     to=request.email,
    #     subject="Login to SplitPro",
    #     body=f"Click here to login: {link}"
    # )

    return {"message": "Magic link sent to email"}


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(request: MagicLinkVerify, db: Session = Depends(get_db)):
    """
    Verify magic link token and login user
    """
    email = verify_magic_link_token(request.token, max_age=3600)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/google")
async def google_login(redirect_uri: Optional[str] = Query(None)):
    """
    Redirect to Google OAuth login

    Replaces NextAuth Google provider initialization
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    from urllib.parse import urlencode

    # Default redirect URI
    if not redirect_uri:
        redirect_uri = f"{settings.CORS_ORIGINS[0]}/auth/callback/google"

    # Build Google OAuth URL
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return {
        "auth_url": auth_url,
        "redirect_uri": redirect_uri
    }


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback

    Replaces NextAuth Google provider callback
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )

    import httpx

    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    'code': code,
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'redirect_uri': f"{settings.CORS_ORIGINS[0]}/auth/callback/google",
                    'grant_type': 'authorization_code'
                }
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )

            tokens = token_response.json()
            access_token = tokens.get('access_token')
            id_token = tokens.get('id_token')

            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )

            userinfo = userinfo_response.json()

            # Extract user data
            email = userinfo.get('email')
            name = userinfo.get('name')
            picture = userinfo.get('picture')
            google_id = userinfo.get('id')

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )

            # Find or create user
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Create new user
                user = User(
                    email=email,
                    name=name or email.split('@')[0],
                    image=picture,
                    currency="USD",
                    preferred_language="en",
                    email_verified=True  # Google verifies emails
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update existing user info
                if name and not user.name:
                    user.name = name
                if picture and not user.image:
                    user.image = picture
                if not user.email_verified:
                    user.email_verified = True
                db.commit()

            # Create or update Google account record
            account = db.query(Account).filter(
                Account.user_id == user.id,
                Account.provider == "google"
            ).first()

            if not account:
                account = Account(
                    id=f"google_{user.id}",
                    user_id=user.id,
                    type="oauth",
                    provider="google",
                    provider_account_id=google_id,
                    access_token=access_token,
                    id_token=id_token,
                    scope="openid email profile"
                )
                db.add(account)
            else:
                account.access_token = access_token
                account.id_token = id_token

            db.commit()

            # Create JWT tokens
            jwt_access_token = create_access_token({"sub": str(user.id)})
            jwt_refresh_token = create_refresh_token({"sub": str(user.id)})

            return TokenResponse(
                access_token=jwt_access_token,
                refresh_token=jwt_refresh_token,
                user=UserResponse.model_validate(user)
            )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth error: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Query(..., description="Refresh token"),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Returns new access and refresh tokens
    """
    from app.core.security import decode_token

    # Decode and validate refresh token
    payload = decode_token(refresh_token)

    if not payload or payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get('sub')

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create new tokens
    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user

    In JWT-based auth, this is mainly for client-side cleanup.
    Could implement token blacklisting here if needed.
    """
    # For now, just return success
    # Client should delete tokens from storage

    # Optional: Implement token blacklisting
    # blacklist_token(access_token, db)

    return None

