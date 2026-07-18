from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from Models.models import CategoryModel, ProfileModel
from Schemas.schemas import CategoryAddSchema
from Core.security import get_current_user
from Database.db import SessionDep


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/")
async def get_categories(
    session: SessionDep,
    user: ProfileModel = Depends(get_current_user)
):
    result = await session.execute(
        select(CategoryModel)
        .where(CategoryModel.user_id == user.id)
    )

    return result.scalars().all()


@router.post("/")
async def add_category(
    data: CategoryAddSchema,
    session: SessionDep,
    user: ProfileModel = Depends(get_current_user)
):

    new_category = CategoryModel(
        user_id=user.id,
        name=data.name,
        emoji=data.emoji
    )

    session.add(new_category)
    await session.commit()

    return {"success": True}