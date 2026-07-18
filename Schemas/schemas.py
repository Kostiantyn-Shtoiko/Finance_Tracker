from pydantic import BaseModel, Field
from typing import Literal


class ProfileRegisterSchema(BaseModel):
    last_name: str
    first_name: str
    phone: str 
    password: str

class ProfileSchema(BaseModel):
    id: int         
    last_name: str  
    first_name: str 
    phone: str      

class ProfileLoginSchema(BaseModel):
    phone: str 
    password: str

class TransactionAddSchema(BaseModel):
    amount: float
    category: str
    title: str | None = Field(max_length=100)
    type: Literal["income", "expense"]
    date: str

class TransactionSchema(BaseModel):
    id: int
    user_id: int
    amount: float
    category: str
    title: str | None = Field(max_length=100)
    type: Literal["income", "expense"]
    date: str

class ProfileUpdateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    password: str | None = None

class CategoryAddSchema(BaseModel):
    name: str
    emoji: str = "📝"  # ← default emoji

class CategorySchema(BaseModel):
    id: int
    name: str
    emoji: str
