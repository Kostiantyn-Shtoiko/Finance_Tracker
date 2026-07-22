from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from Models.models import GoalModel, ProfileModel
from Schemas.schemas import GoalAddSchema
from Database.db import SessionDep
from Core.security import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("/")
async def get_goals(session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(GoalModel).where(GoalModel.user_id == user.id)
    )
    return result.scalars().all()

@router.post("/")
async def add_goal(data: GoalAddSchema, session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    new_goal = GoalModel(
        user_id=user.id,
        title=data.title,
        target_amount=data.target_amount,
        deadline=data.deadline,
        emoji=data.emoji
    )
    session.add(new_goal)
    await session.commit()
    return {"success": True}

@router.put("/{goal_id}/add")
async def add_to_goal(goal_id: int, amount: float, session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(GoalModel).where(GoalModel.id == goal_id, GoalModel.user_id == user.id)
    )
    goal = result.scalar()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found!")
    goal.current_amount += amount
    await session.commit()
    return {"success": True}

@router.delete("/{goal_id}")
async def delete_goal(goal_id: int, session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(GoalModel).where(GoalModel.id == goal_id, GoalModel.user_id == user.id)
    )
    goal = result.scalar()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found!")
    await session.delete(goal)
    await session.commit()
    return {"success": True}