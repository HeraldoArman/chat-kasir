"""Google OAuth2 service using httpx-oauth."""

from datetime import UTC, datetime

from httpx_oauth.clients.google import GoogleOAuth2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_config
from app.models.user import OAuthAccount, OAuthProvider, User
from app.services.auth import create_access_token


def get_google_oauth_client() -> GoogleOAuth2:
    config = get_config()
    return GoogleOAuth2(
        client_id=config.google_oauth.client_id,
        client_secret=config.google_oauth.client_secret,
    )


async def get_or_create_user_from_google(
    db: AsyncSession,
    email: str,
    name: str | None,
    google_user_id: str,
    access_token: str,
    refresh_token: str | None = None,
    expires_at: int | None = None,
) -> tuple[User, bool]:
    result = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == OAuthProvider.GOOGLE,
            OAuthAccount.provider_account_id == google_user_id,
        )
    )
    oauth_account = result.scalar_one_or_none()

    if oauth_account:
        oauth_account.access_token = access_token
        if refresh_token:
            oauth_account.refresh_token = refresh_token
        if expires_at:
            oauth_account.expires_at = datetime.fromtimestamp(expires_at, tz=UTC)
        await db.commit()
        user_result = await db.execute(select(User).where(User.id == oauth_account.user_id))
        found_user = user_result.scalar_one()
        return found_user, False

    user_result = await db.execute(select(User).where(User.username == email))
    existing_user_result = user_result.scalar_one_or_none()

    if existing_user_result is not None:
        user: User = existing_user_result
        new_oauth = OAuthAccount(
            user_id=user.id,
            provider=OAuthProvider.GOOGLE,
            provider_account_id=google_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.fromtimestamp(expires_at, tz=UTC) if expires_at else None,
        )
        db.add(new_oauth)
        await db.commit()
        return user, False

    user = User(
        username=email,
        full_name=name or email.split("@")[0],
        hashed_password="",
    )
    db.add(user)
    await db.flush()

    new_oauth = OAuthAccount(
        user_id=user.id,
        provider=OAuthProvider.GOOGLE,
        provider_account_id=google_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.fromtimestamp(expires_at, tz=UTC) if expires_at else None,
    )
    db.add(new_oauth)
    await db.commit()
    await db.refresh(user)
    return user, True


async def create_jwt_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id))
