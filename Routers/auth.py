from fastapi import APIRouter, FastAPI, Depends, HTTPException, security, status, Response
from sqlalchemy import select
from Models.models import ProfileModel
from Schemas.schemas import ProfileLoginSchema, ProfileRegisterSchema
from Core.security import hash_password, verify_password, create_token
from pydantic import BaseModel
from Database.db import SessionDep

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(data: ProfileRegisterSchema, session: SessionDep):
    
    # 0. check if such a phone already exists
    existing = await session.execute(
        select(ProfileModel).where(ProfileModel.phone == data.phone)
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="Phone already exists!")

    # 1. hash the password
    hashed = hash_password(data.password)
    
    # 2. create a user
    new_user = ProfileModel(
        last_name=data.last_name,
        first_name=data.first_name,
        phone=data.phone,
        password=hashed
    )
    
    # 3. save the user in the database
    session.add(new_user)
    await session.commit()
    
    return {"success": True}
   
@router.post("/login")
async def login(data: ProfileLoginSchema, session: SessionDep):
    # твоя логіка тут!
    pass