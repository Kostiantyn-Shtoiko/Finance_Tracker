from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import asyncio
import httpx



load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

class LoginStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_password = State()

class RegisterStates(StatesGroup):
    waiting_for_last_name = State()
    waiting_for_first_name = State()
    waiting_for_phone = State()
    waiting_for_password = State()

class AddTransactionStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_date = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_tokens = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Hello! I'm your Finance Tracker bot! 💰")

async def main():
    await dp.start_polling(bot)



@dp.message(Command("login")) 
async def login_start(message: types.Message, state: FSMContext):
    await message.answer("Please enter your phone number:")
    await state.set_state(LoginStates.waiting_for_phone)

@dp.message(LoginStates.waiting_for_phone)
async def login_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Please enter your password:")
    await state.set_state(LoginStates.waiting_for_password)

@dp.message(LoginStates.waiting_for_password)
async def login_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    password = message.text
    
    result = await login_user(phone, password)
    
    if "token" in result:
        token = result["token"]
        await message.answer("Logged in! ✅")
        user_tokens[message.from_user.id] = token
    else:
        await message.answer("Wrong phone or password! ❌")
    
    await state.clear()

async def login_user(phone: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/auth/login",
            json={"phone": phone, "password": password}
        )
        return response.json()


@dp.message(Command("register"))
async def register_start(message: types.Message, state: FSMContext):
    await message.answer("Please enter your last name:")
    await state.set_state(RegisterStates.waiting_for_last_name)
@dp.message(RegisterStates.waiting_for_last_name)
async def register_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Please enter your first name:")
    await state.set_state(RegisterStates.waiting_for_first_name)
@dp.message(RegisterStates.waiting_for_first_name)
async def register_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Please enter your phone number:")
    await state.set_state(RegisterStates.waiting_for_phone)
@dp.message(RegisterStates.waiting_for_phone)
async def register_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Please enter your password:")
    await state.set_state(RegisterStates.waiting_for_password)

@dp.message(RegisterStates.waiting_for_password)
async def register_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    
    data = await state.get_data()
    
    result = await register_user(
        data.get("last_name"),
        data.get("first_name"),
        data.get("phone"),
        data.get("password")
    )
    
    if "success" in result:
        await message.answer("Registration complete! ✅")
    else:
        await message.answer("Registration failed! ❌")
    
    await state.clear()

async def register_user(last_name: str, first_name: str, phone: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/auth/register",
            json={
                "last_name": last_name,
                "first_name": first_name,
                "phone": phone,
                "password": password
            }
        )
        return response.json()
    

@dp.message(Command("balance"))
async def balance_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    
    if not token:
        await message.answer("Please /login first!")
        return
    
    balance = await get_balance(token)
    await message.answer(f"Your balance is: {balance['balance']}")

async def get_balance(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8000/transactions/balance",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()



@dp.message(Command("add"))
async def add_transaction_start(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)  
    if not token:
        await message.answer("Please /login first!")
        return
    await message.answer("Please enter the type of transaction:")
    await state.set_state(AddTransactionStates.waiting_for_type)
@dp.message(AddTransactionStates.waiting_for_type)
async def add_transaction_type(message: types.Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("Please enter the amount:")
    await state.set_state(AddTransactionStates.waiting_for_amount)
@dp.message(AddTransactionStates.waiting_for_amount)
async def add_transaction_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await message.answer("Please enter the category:")
    await state.set_state(AddTransactionStates.waiting_for_category)
@dp.message(AddTransactionStates.waiting_for_category)
async def add_transaction_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Please enter the title:")
    await state.set_state(AddTransactionStates.waiting_for_title)
@dp.message(AddTransactionStates.waiting_for_title)
async def add_transaction_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Please enter the date:")
    await state.set_state(AddTransactionStates.waiting_for_date)
@dp.message(AddTransactionStates.waiting_for_date)
async def add_transaction_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    
    data = await state.get_data()
    token = user_tokens.get(message.from_user.id)
    
    result = await add_transaction(token, data)
    
    if "success" in result:
        await message.answer("Transaction added! ✅")
    else:
        await message.answer("Something went wrong! ❌")
    
    await state.clear()

async def add_transaction(token: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/transactions/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "type": data.get("type"),
                "amount": float(data.get("amount")),
                "category": data.get("category"),
                "title": data.get("title"),
                "date": data.get("date")
            }
        )
        return response.json()


@dp.message(Command("history"))
async def history_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    
    if not token:
        await message.answer("Please /login first!")
        return
    
    transactions = await get_transactions(token)
    if not transactions:
        await message.answer("No transactions found.")
        return

    transaction_list = "\n".join([
        f"• {tx['title']} - {tx['amount']} ({tx['category']})" for tx in transactions
    ])
    await message.answer(f"Your transactions:\n{transaction_list}")

async def get_transactions(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:8000/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()





if __name__ == "__main__":
    asyncio.run(main())