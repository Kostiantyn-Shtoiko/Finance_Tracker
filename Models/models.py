from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Column, DateTime, ForeignKey

engine = create_async_engine('sqlite+aiosqlite:///profile.db')

class Base(DeclarativeBase): 
    pass


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str]
    first_name: Mapped[str]
    phone: Mapped[str] 
    password: Mapped[str]

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    amount: Mapped[float]
    category: Mapped[str]
    title: Mapped[str]
    type: Mapped[str]
    date: Mapped[str]

class CategoryModel(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    name: Mapped[str]
    emoji: Mapped[str]