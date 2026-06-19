from Models.models import engine, Base 
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
new_session = AsyncSession(engine, expire_on_commit=False)

async def get_session():
    async with new_session as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]  

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"success": True, "message": "Database setup completed!"}