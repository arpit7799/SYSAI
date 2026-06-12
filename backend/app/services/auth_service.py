from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, TokenResponse
from app.core.logger import log
from datetime import timedelta
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES


async def create_user(data: UserRegister, db: AsyncSession) -> User:
    """Register a new user."""
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Username already taken")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log.info("User registered", username=data.username)
    return user


async def authenticate_user(
    username: str,
    password: str,
    db: AsyncSession
) -> TokenResponse:
    """Authenticate user and return JWT token."""
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid username or password")

    if not user.is_active:
        raise ValueError("Account is disabled")

    token = create_access_token(
        data={"sub": user.username, "admin": user.is_admin}
    )

    log.info("User authenticated", username=username)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        username=user.username,
    )