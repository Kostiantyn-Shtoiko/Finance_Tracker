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



if __name__ == "__main__":
    asyncio.run(main())