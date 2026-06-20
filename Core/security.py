from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from sqlalchemy import select

from Database.db import SessionDep
from Models.models import ProfileModel

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    # "secret123" → "$2b$12$Kx..."
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed) 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), session: SessionDep = ...):
    # 1. decode the token → get user_id
    payload = decode_token(token)
    user_id = payload.get("user_id")
    # 2. find user in database by id
    result = await session.execute(
        select(ProfileModel).where(ProfileModel.id == user_id)
    )
    user = result.scalar()
    # 3. if not found → raise HTTPException
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 4. return user
    return user