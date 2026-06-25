from unittest import result

from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from Core.security import get_current_user
from Database.db import SessionDep
from Models.models import ProfileModel, TransactionModel
from Schemas.schemas import TransactionAddSchema

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/")
async def add_transaction(data: TransactionAddSchema, session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    new_transaction = TransactionModel(
    user_id=user.id,    
    amount=data.amount,        
    category=data.category,      
    title=data.title,
    type=data.type,
    date=data.date
)
    session.add(new_transaction)
    await session.commit()
    
    return {"success": True}

@router.get("/")
async def get_transactions(session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(TransactionModel).where(TransactionModel.user_id == user.id)
    )
    transactions = result.scalars().all()
    return transactions

@router.get("/balance")
async def get_balance(session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(TransactionModel).where(TransactionModel.user_id == user.id)
    )
    transactions = result.scalars().all()
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense
    return {
        "balance": balance, 
        "total_income": total_income, 
        "total_expense": total_expense
    }

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, session: SessionDep, user: ProfileModel = Depends(get_current_user)):
    result = await session.execute(
        select(TransactionModel).where(TransactionModel.id == transaction_id)
    )
    transaction = result.scalar()

    if not transaction:
        raise HTTPException(status_code=404, detail="Not found")

    if transaction.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your transaction!")

    await session.delete(transaction)
    await session.commit()
    return {"success": True}