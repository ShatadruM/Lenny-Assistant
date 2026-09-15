from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import bcrypt
from app.db.session import get_db
from app.db.models import User
import uuid

router = APIRouter()

class AuthRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(request: AuthRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    stmt = select(User).where(User.username == request.username)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    # Hash password using direct bcrypt to avoid passlib incompatibilities
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), salt).decode('utf-8')
    
    new_user = User(
        username=request.username,
        password_hash=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"user_id": new_user.id, "username": new_user.username}

@router.post("/login")
async def login(request: AuthRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == request.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
        
    # Verify password
    is_valid = bcrypt.checkpw(
        request.password.encode('utf-8'), 
        user.password_hash.encode('utf-8')
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
        
    return {"user_id": user.id, "username": user.username}
