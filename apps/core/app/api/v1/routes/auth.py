from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_config
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.oauth import (
    create_jwt_for_user,
    get_google_oauth_client,
    get_or_create_user_from_google,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        whatsapp_number=user_in.whatsapp_number,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/login/google")
async def login_google() -> RedirectResponse:
    google_oauth = get_google_oauth_client()
    config = get_config()
    authorization_url = await google_oauth.get_authorization_url(
        redirect_uri=config.google_oauth.redirect_uri,
    )
    return RedirectResponse(url=authorization_url)


@router.get("/callback/google")
async def callback_google(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> Token:
    google_oauth = get_google_oauth_client()
    config = get_config()
    token = await google_oauth.get_access_token(
        code=code,
        redirect_uri=config.google_oauth.redirect_uri,
    )
    user_info = await google_oauth.get_profile(token["access_token"])

    user, _ = await get_or_create_user_from_google(
        db=db,
        email=user_info["email"],
        name=user_info.get("name"),
        google_user_id=user_info["sub"],
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        expires_at=token.get("expires_at"),
    )

    access_token = await create_jwt_for_user(user)
    return Token(access_token=access_token)
