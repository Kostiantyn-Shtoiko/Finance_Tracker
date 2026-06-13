from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey

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


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    amount: Mapped[float]
    category: Mapped[str]
    title: Mapped[str]
    type: Mapped[str]
    date: Mapped[str]
