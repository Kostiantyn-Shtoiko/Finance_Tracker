from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from Models.models import ProfileModel
from Schemas.schemas import ProfileLoginSchema, ProfileRegisterSchema
from Core.security import hash_password, verify_password, create_token
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
    
    # 1. find user
    result = await session.execute(
        select(ProfileModel).where(ProfileModel.phone == data.phone)
    )
    user = result.scalar()
    
    # 2. if not found
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    
    # 3. check password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password!")
    
    # 4. create a token
    token = create_token({"user_id": user.id})
    
    # 5. return token
    return {"token": token}