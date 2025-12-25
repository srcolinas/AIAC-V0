"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new account with username, email, and password.
    """
    # Check if username exists
    existing = await AuthService.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing = await AuthService.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate and get access token.
    
    Provide username and password to receive a JWT token.
    """
    user = await AuthService.authenticate_user(
        db, 
        credentials.username, 
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns the authenticated user's information.
    """
    return current_user


@router.get("/leaderboard", response_model=list[UserResponse])
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """
    Get top players leaderboard.
    
    Returns users sorted by games won.
    """
    from sqlalchemy import select
    from app.models.user import User
    
    result = await db.execute(
        select(User)
        .order_by(User.games_won.desc(), User.total_points.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

