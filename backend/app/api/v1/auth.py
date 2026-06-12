from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import create_user, authenticate_user
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core.security import decode_token
from app.db.models import User
from sqlalchemy import select

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency — validates JWT and returns current user.
    Use this in any route that needs authentication:
    current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


@router.post(
    "/auth/register",
    response_model=UserResponse,
    tags=["Auth"],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new SYSAI user."""
    try:
        user = await create_user(data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/auth/token",
    response_model=TokenResponse,
    tags=["Auth"],
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and receive a JWT access token."""
    try:
        return await authenticate_user(data.username, data.password, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["Auth"],
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user