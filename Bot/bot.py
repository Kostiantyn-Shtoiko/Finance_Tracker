from email.mime import message
import profile
from unittest import result
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import asyncio
import httpx
import re

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://financetracker-production-d18b.up.railway.app")
# BASE_URL = os.getenv("BASE_URL", "http://api:8000")

# ══════════════════════════════════════
#              STATES
# ══════════════════════════════════════

class LoginStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_password = State()

class RegisterStates(StatesGroup):
    waiting_for_last_name = State()
    waiting_for_first_name = State()
    waiting_for_phone = State()
    waiting_for_password = State()
    waiting_for_weak_password_confirmation = State()

class AddTransactionStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_date = State()

class EditProfileStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()
    waiting_for_old_password = State()
    waiting_for_new_password = State()
    waiting_for_weak_password_confirmation = State()

class ReminderStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_timezone = State()

class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()
    waiting_for_delete = State()

class GoalStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_emoji = State()
    waiting_for_amount = State()
    waiting_for_deadline = State()
    waiting_for_add_amount = State()
# ══════════════════════════════════════
#              BOT & DISPATCHER
# ══════════════════════════════════════

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_tokens = {}

scheduler = AsyncIOScheduler()
user_reminders = {}

TIMEZONES = {
    "🇺🇦 Kyiv (UTC+3)": "Europe/Kyiv",
    "🇭🇷 Zagreb (UTC+2)": "Europe/Zagreb",
    "🇬🇧 London (UTC+1)": "Europe/London",
    "🌍 Other (UTC+0)": "UTC"
}

user_timezones = {}
# ══════════════════════════════════════
#              KEYBOARDS
# ══════════════════════════════════════

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Register"),
                KeyboardButton(text="🔑 Login")
            ],
            [
                KeyboardButton(text="💰 Balance"),
                KeyboardButton(text="➕ Add Transaction")
            ],
            [
                KeyboardButton(text="📊 History"),
                KeyboardButton(text="ℹ️ Help")
            ],
            [
                KeyboardButton(text="🎯 Goals"),
                KeyboardButton(text="👤 Profile"),
            ]
        ],
        resize_keyboard=True
    )

def get_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💰 Income"),
                KeyboardButton(text="💸 Expense")
            ],
            [
                KeyboardButton(text="❌ Cancel")
            ]
        ],
        resize_keyboard=True
    )

def get_category_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🍔 Food"),
                KeyboardButton(text="💼 Salary")
            ],
            [
                KeyboardButton(text="🚗 Transport"),
                KeyboardButton(text="🏠 Housing")
            ],
            [
                KeyboardButton(text="🎮 Entertainment"),
                KeyboardButton(text="📝 Other")
            ],
            [
                KeyboardButton(text="❌ Cancel")
            ]
        ],
        resize_keyboard=True
    )


def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⬅️ Back")
            ]
        ],
        resize_keyboard=True
    )

def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Skip")]
        ],
        resize_keyboard=True
    )

def get_auth_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Register"),
                KeyboardButton(text="🔑 Login")
            ]
        ],
        resize_keyboard=True
    )

def get_password_warning_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Keep password"),
                KeyboardButton(text="🔄 Change password")
            ]
        ],
        resize_keyboard=True
    )

def get_profile_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [   
                KeyboardButton(text="📊 Statistics"),
                KeyboardButton(text="⚙️ Settings")
            ],
            [   
                KeyboardButton(text="ℹ️ About"),
            ],
            [   
                KeyboardButton(text="⬅️ Back"),
            ]
        ],
        resize_keyboard=True
    )

def get_settings_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✏️ Edit Name"),
                KeyboardButton(text="🔑 Change Password")
            ],
            [
                KeyboardButton(text="📱 Change Phone"),
                KeyboardButton(text="✏️ Edit Categories")
            ],
            [
                KeyboardButton(text="🌍 Change Language"),
                KeyboardButton(text="🔔 Reminder time")
            ],
            [
                KeyboardButton(text="🚪 Logout"),
                KeyboardButton(text="🗑 Delete Account"),
            ]
        ],
        resize_keyboard=True
    )

def get_edit_name_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✏️ Edit First Name"),
                KeyboardButton(text="✏️ Edit Last Name")
            ],
            [
                KeyboardButton(text="⬅️ Back")
            ]
        ],
        resize_keyboard=True
    )

def get_reminder_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Add Reminder"),
                KeyboardButton(text="📋 My Reminders")
            ],
            [
                KeyboardButton(text="🗑️ Delete Reminder"),
                KeyboardButton(text="⬅️ Back")
            ]
        ],
        resize_keyboard=True
    )

def get_timezone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇦 Kyiv (UTC+3)"),
                KeyboardButton(text="🇭🇷 Zagreb (UTC+2)")
            ],
            [
                KeyboardButton(text="🇬🇧 London (UTC+1)"),
                KeyboardButton(text="🌍 Other (UTC+0)")
            ],
            [
                KeyboardButton(text="❌ Cancel")
            ]
        ],
        resize_keyboard=True
    )

def get_goals_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🎯 My Goals"),
                KeyboardButton(text="➕ Add Goal")
            ],
            [KeyboardButton(text="⬅️ Back")]
        ],
        resize_keyboard=True
    )
# ══════════════════════════════════════
#              API FUNCTIONS
# ══════════════════════════════════════

async def login_user(phone: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"phone": phone, "password": password}
        )
        return response.json()

async def register_user(last_name: str, first_name: str, phone: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "last_name": last_name,
                "first_name": first_name,
                "phone": phone,
                "password": password
            }
        )
        return response.json()

async def get_balance(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/transactions/balance",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

async def get_transactions(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

async def add_transaction(token: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/transactions/",
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

async def delete_transaction_api(token: str, transaction_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

async def get_me(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

async def update_profile_api(token: str, first_name: str = None, last_name: str = None, phone: str = None, password: str = None):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "password": password
            }
        )
        return response.json()
    
async def delete_account_api(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
async def get_categories_api(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/categories/",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        return response.json()

async def add_category_api(token: str, name: str, emoji: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/categories/",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "emoji": emoji}
        )
        return response.json()

async def delete_category_api(token: str, category_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/categories/{category_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
async def get_goals_api(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient() as session:
        response = await session.get(
            f"{BASE_URL}/goals/",
            headers=headers
        )
        return response.json()
    
async def add_goal_api(token, data):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient() as session:
        response = await session.post(
            f"{BASE_URL}/goals/",
            headers=headers,
            json=data
        )
        return response.json()
    
async def delete_goal_api(token, goal_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient() as session:
        response = await session.delete(
            f"{BASE_URL}/goals/{goal_id}",
            headers=headers
        )
        return response.json()
# ══════════════════════════════════════
#              START
# ══════════════════════════════════════

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Welcome to Finance Tracker!\nChoose an option:",
        reply_markup=get_main_keyboard()
    )

# ══════════════════════════════════════
#              CANCEL
# ══════════════════════════════════════

@dp.message(F.text == "❌ Cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Cancelled. Choose an option:",
        reply_markup=get_main_keyboard()
    )

# ══════════════════════════════════════
#              BACK
# ══════════════════════════════════════

@dp.message(F.text == "⬅️ Back")
async def back_handler(message: types.Message):
    await message.answer(
        "🏠 Main Menu",
        reply_markup=get_main_keyboard()
    )

# ══════════════════════════════════════
#              LOGIN
# ══════════════════════════════════════

@dp.message(Command("login"))
@dp.message(F.text == "🔑 Login")
async def login_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Please enter your phone number:",
        reply_markup=ReplyKeyboardRemove()
    )
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
        user_tokens[message.from_user.id] = result["token"]
        profile = await get_me(result["token"])
        name = profile.get("first_name", "Friend")
        await message.answer(f"Welcome back, {name}! 👋✅", reply_markup=get_main_keyboard())
    else:
        await message.answer("Wrong phone or password! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#              REGISTER
# ══════════════════════════════════════

@dp.message(Command("register"))
@dp.message(F.text == "📝 Register")
async def register_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Please enter your last name:",
        reply_markup=ReplyKeyboardRemove()
    )
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
    if not message.text.isdigit():
        await message.answer("❌ Phone must contain only numbers! Try again:")
        return
    if not (10 <= len(message.text) <= 13):
        await message.answer("❌ Phone must be 10-13 digits! Try again:")
        return
    await state.update_data(phone=message.text)
    await message.answer("Please enter your password:")
    await state.set_state(RegisterStates.waiting_for_password)

@dp.message(RegisterStates.waiting_for_password)
async def register_password(message: types.Message, state: FSMContext):
    password = message.text

    if not is_strong_password(password):
        await state.update_data(password=password)

        await message.answer(
            "⚠️ Weak password!\n\n"
            "Your password should contain:\n"
            "• At least 8 characters\n"
            "• One uppercase letter\n"
            "• One lowercase letter\n"
            "• One number\n\n"
            "Do you want to keep this password?",
            reply_markup=get_password_warning_keyboard()
        )

        await state.set_state(RegisterStates.waiting_for_weak_password_confirmation)
        return

    await state.update_data(password=password)

    data = await state.get_data()
    result = await register_user(
        data["last_name"],
        data["first_name"],
        data["phone"],
        data["password"]
    )

    if result.get("success"):
        login_result = await login_user(data["phone"], data["password"])
    
    if "token" in login_result:
        user_tokens[message.from_user.id] = login_result["token"]
        profile = await get_me(login_result["token"])
        name = profile.get("first_name", "Friend")
        await message.answer(
            f"Registration successful! 🎉\n"
            f"Welcome, {name}! You are now logged in! ✅",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Registration successful! 🎉\nPlease login manually.",
            reply_markup=get_main_keyboard()
        )
    await state.clear()

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False

    if " " in password:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    return True

@dp.message(RegisterStates.waiting_for_weak_password_confirmation)
async def weak_password_confirmation(message: types.Message, state: FSMContext):
    if message.text == "🔄 Change password":
        await message.answer(
            "Enter a new password:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(RegisterStates.waiting_for_password)
        return

    if message.text == "✅ Keep password":
        data = await state.get_data()

        result = await register_user(
            data["last_name"],
            data["first_name"],
            data["phone"],
            data["password"]
        )

        if result.get("success"):
            login_result = await login_user(data["phone"], data["password"])
    
        if "token" in login_result:
            user_tokens[message.from_user.id] = login_result["token"]
            profile = await get_me(login_result["token"])
            name = profile.get("first_name", "Friend")
            await message.answer(
                f"Registration successful! 🎉\n"
                f"Welcome, {name}! You are now logged in! ✅",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                f"Registration failed: {result.get('detail', 'Unknown error')}",
                reply_markup=get_main_keyboard()
            )
        await state.clear()
        return
    
    await message.answer("Please choose one of the buttons.")

# ══════════════════════════════════════
#              BALANCE
# ══════════════════════════════════════

@dp.message(Command("balance"))
@dp.message(F.text == "💰 Balance")
async def balance_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
    reply_markup=get_auth_keyboard())
        return

    balance = await get_balance(token)
    text = (
        f"💰 Your Finance Summary\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📈 Income:  +{balance['total_income']:.2f}\n"
        f"📉 Expense: -{balance['total_expense']:.2f}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💵 Balance:  {balance['balance']:.2f}"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

# ══════════════════════════════════════
#              HISTORY
# ══════════════════════════════════════

ITEMS_PER_PAGE = 5

@dp.message(Command("history"))
@dp.message(F.text == "📊 History")
async def history_command(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
    reply_markup=get_auth_keyboard())
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 All", callback_data="filter_all"),
            InlineKeyboardButton(text="💰 Income", callback_data="filter_income"),
            InlineKeyboardButton(text="💸 Expense", callback_data="filter_expense")
        ]
    ])
    await message.answer("Choose filter:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("filter_"))
async def filter_history(callback_query: types.CallbackQuery, state: FSMContext):
    filter_type = callback_query.data.replace("filter_", "")
    token = user_tokens.get(callback_query.from_user.id)
    
    transactions = await get_transactions(token)
    
    # Фільтруємо!
    if filter_type == "income":
        filtered = [tx for tx in transactions if tx['type'] == "income"]
    elif filter_type == "expense":
        filtered = [tx for tx in transactions if tx['type'] == "expense"]
    else:
        filtered = transactions  # all
    
    if not filtered:
        await callback_query.message.answer("No transactions found! 📭")
        await callback_query.answer()
        return
    
    await state.update_data(transactions=filtered, page=0)
    await show_history_page(callback_query, filtered, page=0)
    await callback_query.answer()


async def show_history_page(message_or_callback, transactions, page):
    total_pages = (len(transactions) - 1) // ITEMS_PER_PAGE + 1
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_transactions = transactions[start:end]

    header = f"📊 History (Page {page + 1}/{total_pages})\n━━━━━━━━━━━━━━━━━━━━"
    
    if isinstance(message_or_callback, types.CallbackQuery):
        await message_or_callback.message.answer(header)
    else:
        await message_or_callback.answer(header)

    for i, tx in enumerate(page_transactions, start + 1):
        emoji = "📈" if tx['type'] == "income" else "📉"
        text = (
            f"{i}. {emoji} {tx['title']}\n"
            f"   📁 {tx['category']} | 💵 {tx['amount']:.2f}\n"
            f"   📅 {tx['date']}"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_{tx['id']}"),
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_{tx['id']}")
            ]
        ])
        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.answer(text, reply_markup=keyboard)
        else:
            await message_or_callback.answer(text, reply_markup=keyboard)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="▶️ Next", callback_data=f"page_{page+1}"))

    if buttons:
        nav_keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.answer("━━━━━━━━━━━━━━━━━━━━", reply_markup=nav_keyboard)
        else:
            await message_or_callback.answer("━━━━━━━━━━━━━━━━━━━━", reply_markup=nav_keyboard)

@dp.callback_query(lambda c: c.data.startswith("page_"))
async def change_page(callback_query: types.CallbackQuery, state: FSMContext):
    page = int(callback_query.data.replace("page_", ""))
    
    data = await state.get_data()
    transactions = data.get("transactions")
    
    await state.update_data(page=page)
    await show_history_page(callback_query, transactions, page)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_transaction(callback_query: types.CallbackQuery):
    transaction_id = callback_query.data.replace("delete_", "")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_delete_{transaction_id}"),
            InlineKeyboardButton(text="❌ No", callback_data="cancel_delete")
        ]
    ])
    await callback_query.message.answer(
        "Are you sure you want to delete this transaction?",
        reply_markup=keyboard
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def confirm_delete(callback_query: types.CallbackQuery):
    transaction_id = callback_query.data.replace("confirm_delete_", "")
    token = user_tokens.get(callback_query.from_user.id)
    
    result = await delete_transaction_api(token, transaction_id)
    
    if "success" in result:
        await callback_query.message.answer("Transaction deleted! ✅")
    else:
        await callback_query.message.answer("Something went wrong! ❌")
    
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "cancel_delete")
async def cancel_delete(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Cancelled! ❌")
    await callback_query.answer()

# ══════════════════════════════════════
#              ADD TRANSACTION
# ══════════════════════════════════════

@dp.message(Command("add"))
@dp.message(F.text == "➕ Add Transaction")
async def add_transaction_start(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return
    await message.answer(
        "Choose transaction type:",
        reply_markup=get_type_keyboard()
    )
    await state.set_state(AddTransactionStates.waiting_for_type)

@dp.message(F.text.in_(["💰 Income", "💸 Expense"]), AddTransactionStates.waiting_for_type)
async def add_transaction_type(message: types.Message, state: FSMContext):
    transaction_type = "income" if message.text == "💰 Income" else "expense"
    await state.update_data(type=transaction_type)
    await message.answer(
        "Please enter the amount:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddTransactionStates.waiting_for_amount)

@dp.message(AddTransactionStates.waiting_for_amount)
async def add_transaction_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Amount must be > 0! Try again:")
            return
    except ValueError:
        await message.answer("❌ Enter a number! Example: 100.50")
        return

    await state.update_data(amount=amount)
    
    token = user_tokens.get(message.from_user.id)
    custom_categories = await get_categories_api(token)
    keyboard_rows = [
        [KeyboardButton(text="🍔 Food"), KeyboardButton(text="💼 Salary")],
        [KeyboardButton(text="🚗 Transport"), KeyboardButton(text="🏠 Housing")],
        [KeyboardButton(text="🎮 Entertainment"), KeyboardButton(text="📝 Other")],
    ]
    
    for cat in custom_categories:
        keyboard_rows.append([
            KeyboardButton(text=f"{cat['emoji']} {cat['name']}")
        ])
    
    keyboard_rows.append([KeyboardButton(text="❌ Cancel")])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )
    
    await message.answer("Choose category:", reply_markup=keyboard)
    await state.set_state(AddTransactionStates.waiting_for_category)

@dp.message(AddTransactionStates.waiting_for_category)
async def add_transaction_category(message: types.Message, state: FSMContext):
    standard = ["🍔 Food", "💼 Salary", "🚗 Transport",
                "🏠 Housing", "🎮 Entertainment", "📝 Other"]
    
    if message.text in standard:
        category = message.text.split(" ", 1)[1].lower()
    else:
        category = message.text.split(" ", 1)[1] if " " in message.text else message.text
    
    await state.update_data(category=category)
    await message.answer(
        "📝 Enter a title\n\n"
        "Or press ⏭ Skip if you don't want to add one.",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(AddTransactionStates.waiting_for_title)

@dp.message(AddTransactionStates.waiting_for_title)
async def add_transaction_title(message: types.Message, state: FSMContext):
    title = "" if message.text == "⏭ Skip" else message.text
    await state.update_data(title=title)
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="📅 Today"),
            KeyboardButton(text="✏️ Enter manually")
        ],
    ], 
    resize_keyboard=True
    )
    
    await message.answer("Choose date:", reply_markup=keyboard)
    await state.set_state(AddTransactionStates.waiting_for_date)

@dp.message(F.text.in_(["📅 Today", "✏️ Enter manually"]), AddTransactionStates.waiting_for_date)
async def choose_date(message: types.Message, state: FSMContext):
    if message.text == "📅 Today":
        today = datetime.now().strftime("%Y-%m-%d")
        await state.update_data(date=today)
        
        data = await state.get_data()
        token = user_tokens.get(message.from_user.id)
        result = await add_transaction(token, data)
        
        if "success" in result:
            token = user_tokens.get(message.from_user.id)
            balance = await get_balance(token) 
            await message.answer(f"Transaction added! ✅\n"
                                 f"You balance has been updated 💰: {balance['balance']:.2f}", 
                                 reply_markup=get_main_keyboard())
        else:
            await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
        
        await state.clear()
    else:
        await message.answer(
            "Enter date (YYYY-MM-DD):\nExample: 2024-01-15",
            reply_markup=ReplyKeyboardRemove()
        )

@dp.message(AddTransactionStates.waiting_for_date)
async def add_transaction_date(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Wrong format! Use: YYYY-MM-DD")
        return

    await state.update_data(date=message.text)
    data = await state.get_data()
    token = user_tokens.get(message.from_user.id)
    result = await add_transaction(token, data)

    if "success" in result:
        token = user_tokens.get(message.from_user.id)
        balance = await get_balance(token) 
        await message.answer(f"Transaction added! ✅\n"
                                 f"You balance has been updated 💰: {balance['balance']:.2f}", 
                                 reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#              Settings
# ══════════════════════════════════════

@dp.message(Command("settings"))
@dp.message(F.text == "⚙️ Settings")

async def settings_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return
    
    await message.answer(
        "⚙️ Settings Menu",
        reply_markup=get_settings_keyboard()
    )
# ══════════════════════════════════════
#              Profile
# ══════════════════════════════════════

@dp.message(Command("profile"))
@dp.message(F.text == "👤 Profile")

async def profile_command(message: types.Message, state: FSMContext):

    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return
    
    user_info = await get_me(token) 
    await message.answer(
        f"👋 Welcome {user_info['first_name']} {user_info['last_name']}!\n")
    
    balance = await get_balance(token)
    text = (
        f"👤 Profile\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💵 Balance:  {balance['balance']:.2f}\n"
        f"Phone: {user_info['phone']}\n"
        f"📅 Registered: {user_info['created_at']}"
        f"━━━━━━━━━━━━━━━\n"
    )
    await message.answer(text, reply_markup=get_profile_keyboard())

# ══════════════════════════════════════
#            Edit Password
# ══════════════════════════════════════

@dp.message(F.text == "🔑 Change Password")
async def change_password_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter your current password:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditProfileStates.waiting_for_old_password)

@dp.message(EditProfileStates.waiting_for_old_password)
async def verify_old_password(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    
    profile = await get_me(token)
    phone = profile.get("phone")
    
    result = await login_user(phone, message.text)
    
    if "token" not in result:
        await message.answer("❌ Wrong password! Try again:")
        return
    
    await message.answer("Enter new password:")
    await state.set_state(EditProfileStates.waiting_for_new_password)

@dp.message(EditProfileStates.waiting_for_new_password)
async def save_new_password(message: types.Message, state: FSMContext):
    if not is_strong_password(message.text):
        await state.update_data(password=message.text)
        await message.answer(
            "⚠️ Weak password!\n\n"
            "• At least 8 characters\n"
            "• One uppercase letter\n"
            "• One lowercase letter\n"
            "• One number\n\n"
            "Do you want to keep this password?",
            reply_markup=get_password_warning_keyboard()
        )
        await state.set_state(EditProfileStates.waiting_for_weak_password_confirmation)
        return

    token = user_tokens.get(message.from_user.id)
    result = await update_profile_api(token, password=message.text)

    if "success" in result:
        await message.answer("✅ Password changed!", reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())

    await state.clear()

@dp.message(EditProfileStates.waiting_for_weak_password_confirmation)
async def weak_password_confirmation_edit(message: types.Message, state: FSMContext):
    if message.text == "🔄 Change password":
        await message.answer(
            "Enter a new password:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(EditProfileStates.waiting_for_new_password)
        return

    if message.text == "✅ Keep password":
        data = await state.get_data()
        token = user_tokens.get(message.from_user.id)
        
        result = await update_profile_api(token, password=data.get("password"))
        
        if "success" in result:
            await message.answer("✅ Password changed!", reply_markup=get_main_keyboard())
        else:
            await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
        
        await state.clear()
        return

    await message.answer("Please choose one of the buttons.")
# ══════════════════════════════════════
#            Edit Phone
# ══════════════════════════════════════
@dp.message(F.text == "📱 Change Phone")
async def edit_phone_command(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter new phone number:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditProfileStates.waiting_for_phone)

@dp.message(EditProfileStates.waiting_for_phone)
async def save_phone_command(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Phone must contain only numbers! Try again:")
        return
    if not (10 <= len(message.text) <= 13):
        await message.answer("❌ Phone must be 10-13 digits! Try again:")
        return
    
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return

    result = await update_profile_api(token, phone=message.text)

    if "success" in result:
        await message.answer(f"✅ Phone number updated to: {message.text}!", reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#            Edit Name
# ══════════════════════════════════════

@dp.message(F.text == "✏️ Edit Name")
async def edit_name_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return
    
    user_info = await get_me(token) 
    await message.answer(
        f"👋 Welcome {user_info['first_name']} {user_info['last_name']}!\n"
        f" What do you want to replace?\n",
        reply_markup=get_edit_name_keyboard()
    )

@dp.message(F.text == "✏️ Edit First Name")
async def edit_first_name_command(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter new first name:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditProfileStates.waiting_for_first_name)

@dp.message(EditProfileStates.waiting_for_first_name)
async def save_first_name(message: types.Message, state: FSMContext):

    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return

    result = await update_profile_api(token, first_name=message.text)
    
    if "success" in result:
        await message.answer(f"✅ First name updated to: {message.text}!", reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await state.clear()

@dp.message(F.text == "✏️ Edit Last Name")
async def edit_last_name_command(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter new last name:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditProfileStates.waiting_for_last_name)

@dp.message(EditProfileStates.waiting_for_last_name)
async def save_last_name_command(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ You are not logged in!\nPlease register or login:",
                            reply_markup=get_auth_keyboard())
        return

    result = await update_profile_api(token, last_name=message.text)
    
    if "success" in result:
        await message.answer(f"✅ Last name updated to: {message.text}!", reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await state.clear()

# ══════════════════════════════════════
#             Delete Account
# ══════════════════════════════════════
@dp.message(F.text == "🗑 Delete Account")
async def delete_account_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Yes, delete"),
                KeyboardButton(text="❌ No, cancel")
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "⚠️ Are you sure?\n\n"
        "This will permanently delete your account\n"
        "and ALL your transactions!\n\n"
        "This action CANNOT be undone! 🔴",
        reply_markup=keyboard
    )

@dp.message(F.text == "✅ Yes, delete")
async def confirm_delete_account(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ Not logged in!", reply_markup=get_auth_keyboard())
        return
    
    result = await delete_account_api(token)
    
    if "success" in result:
        user_tokens.pop(message.from_user.id, None)
        await state.clear()
        await message.answer(
            "🗑 Account deleted successfully!\n"
            "Sorry to see you go! 👋",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())

@dp.message(F.text == "❌ No, cancel")
async def cancel_delete_account(message: types.Message):
    await message.answer(
        "❌ Cancelled!",
        reply_markup=get_main_keyboard()
    )

# ══════════════════════════════════════
#              Goals
# ══════════════════════════════════════
@dp.message(F.text == "🎯 Goals")
async def show_goals(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ Please login first!", reply_markup=get_auth_keyboard())
        return
    
    goals = await get_goals_api(token)
    
    if not isinstance(goals, list) or not goals:
        await message.answer(
            "No goals yet! 📭\nAdd your first goal!",
            reply_markup=get_goals_keyboard() 
        )
        return
    
    await message.answer(
        "🎯 Your Goals:",
        reply_markup=get_goals_keyboard()  
    )
    
    for goal in goals:
        progress = make_progress_bar(goal['current_amount'], goal['target_amount'])
        remaining = goal['target_amount'] - goal['current_amount']
        
        deadline = datetime.strptime(goal['deadline'], "%Y-%m-%d")
        days_left = (deadline - datetime.now()).days
        daily_needed = remaining / days_left if days_left > 0 else 0
        
        text = (
            f"{goal['emoji']} {goal['title']}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 Target:    {goal['target_amount']:.2f}\n"
            f"💰 Saved:     {goal['current_amount']:.2f}\n"
            f"📉 Remaining: {remaining:.2f}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{progress}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📅 Days left: {days_left}\n"
            f"💸 Daily: {daily_needed:.2f}/day"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Money", callback_data=f"goal_add_{goal['id']}"),
                InlineKeyboardButton(text="🗑️ Delete", callback_data=f"goal_delete_{goal['id']}")
            ]
        ])
        await message.answer(text, reply_markup=keyboard)

def make_progress_bar(current: float, target: float) -> str:
    percentage = min(current / target * 100, 100)
    filled = int(percentage / 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {percentage:.1f}%"

@dp.message(F.text == "🎯 My Goals")
async def show_my_goals(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ Please login first!", reply_markup=get_auth_keyboard())
        return

    goals = await get_goals_api(token)

    if not isinstance(goals, list) or not goals:
        await message.answer(
            "No goals yet! 📭\nAdd your first goal!",
            reply_markup=get_goals_keyboard()
        )
        return

    await message.answer(
        "🎯 Your Goals:",
        reply_markup=get_goals_keyboard()
    )

    for goal in goals:
        progress = make_progress_bar(goal['current_amount'], goal['target_amount'])
        remaining = goal['target_amount'] - goal['current_amount']

        deadline = datetime.strptime(goal['deadline'], "%Y-%m-%d")
        days_left = (deadline - datetime.now()).days
        daily_needed = remaining / days_left if days_left > 0 else 0

        text = (
            f"{goal['emoji']} {goal['title']}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 Target:    {goal['target_amount']:.2f}\n"
            f"💰 Saved:     {goal['current_amount']:.2f}\n"
            f"📉 Remaining: {remaining:.2f}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{progress}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📅 Days left: {days_left}\n"
            f"💸 Daily: {daily_needed:.2f}/day"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Money", callback_data=f"goal_add_{goal['id']}"),
                InlineKeyboardButton(text="🗑️ Delete", callback_data=f"goal_delete_{goal['id']}")
            ]
        ])
        await message.answer(text, reply_markup=keyboard)

def make_progress_bar(current: float, target: float) -> str:
    percentage = min(current / target * 100, 100)
    filled = int(percentage / 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {percentage:.1f}%"

@dp.message(F.text == "➕ Add Goal")
async def add_goal_start(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("⚠️ Please login first!", reply_markup=get_auth_keyboard())
        return
    await message.answer(
        "Enter goal title:\nExample: Buy a laptop 💻",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(GoalStates.waiting_for_title)

@dp.message(GoalStates.waiting_for_title)
async def save_goal_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        "Enter emoji for goal:\nExample: 💻\n\n"
        "Or press ⏭ Skip for default 🎯",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(GoalStates.waiting_for_emoji)

@dp.message(GoalStates.waiting_for_emoji)
async def save_goal_emoji(message: types.Message, state: FSMContext):
    emoji = "🎯" if message.text == "⏭ Skip" else message.text
    await state.update_data(emoji=emoji)
    await message.answer(
        "Enter target amount:\nExample: 1000",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(GoalStates.waiting_for_amount)

@dp.message(GoalStates.waiting_for_amount)
async def save_goal_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Amount must be > 0! Try again:")
            return
    except ValueError:
        await message.answer("❌ Enter a number! Example: 1000")
        return
    
    await state.update_data(target_amount=amount)
    await message.answer(
        "Enter deadline (YYYY-MM-DD):\nExample: 2024-12-31"
    )
    await state.set_state(GoalStates.waiting_for_deadline)

@dp.message(GoalStates.waiting_for_deadline)
async def save_goal_deadline(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Wrong format! Use: YYYY-MM-DD\nExample: 2024-12-31")
        return
    
    data = await state.get_data()
    token = user_tokens.get(message.from_user.id)
    
    result = await add_goal_api(token, {
        "title": data.get("title"),
        "emoji": data.get("emoji"),
        "target_amount": data.get("target_amount"),
        "deadline": message.text
    })
    
    if "success" in result:
        await message.answer(
            f"✅ Goal '{data.get('title')}' created!\n"
            f"Target: {data.get('target_amount'):.2f}\n"
            f"Deadline: {message.text}",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("goal_add_"))
async def goal_add_money_start(callback_query: types.CallbackQuery, state: FSMContext):
    goal_id = callback_query.data.replace("goal_add_", "")
    await state.update_data(goal_id=goal_id)
    await callback_query.message.answer(
        "Enter amount to add:\nExample: 100"
    )
    await state.set_state(GoalStates.waiting_for_add_amount)
    await callback_query.answer()

@dp.message(GoalStates.waiting_for_add_amount)
async def save_goal_add_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Amount must be > 0! Try again:")
            return
    except ValueError:
        await message.answer("❌ Enter a number! Example: 100")
        return
    
    data = await state.get_data()
    goal_id = data.get("goal_id")
    token = user_tokens.get(message.from_user.id)
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/goals/{goal_id}/add",
            headers={"Authorization": f"Bearer {token}"},
            params={"amount": amount}
        )
        result = response.json()
    
    if "success" in result:
        await message.answer(
            f"✅ Added {amount:.2f} to goal!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("goal_delete_"))
async def goal_delete(callback_query: types.CallbackQuery):
    goal_id = int(callback_query.data.replace("goal_delete_", ""))
    token = user_tokens.get(callback_query.from_user.id)
    
    result = await delete_goal_api(token, goal_id)
    
    if "success" in result:
        await callback_query.message.answer("✅ Goal deleted!", reply_markup=get_main_keyboard())
    else:
        await callback_query.message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await callback_query.answer()
# ══════════════════════════════════════
#             Reminder Time
# ══════════════════════════════════════
@dp.message(F.text == "🔔 Reminder time")
async def reminder_menu(message: types.Message):
    await message.answer(
        "🔔 Reminder Menu\n"
        "Set a daily reminder to record your expenses!",
        reply_markup=get_reminder_keyboard()
    )

@dp.message(F.text == "➕ Add Reminder")
async def add_reminder_start(message: types.Message, state: FSMContext):
    await message.answer(
        "First, choose your timezone:",
        reply_markup=get_timezone_keyboard()
    )
    await state.set_state(ReminderStates.waiting_for_timezone)

@dp.message(F.text.in_(TIMEZONES.keys()), ReminderStates.waiting_for_timezone)
async def save_timezone(message: types.Message, state: FSMContext):
    timezone = TIMEZONES[message.text]
    user_timezones[message.from_user.id] = timezone
    await state.update_data(timezone=timezone)
    
    await message.answer(
        f"✅ Timezone set!\n\n"
        f"Now enter reminder time (HH:MM):\n"
        f"Example: 20:00",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ReminderStates.waiting_for_time)

@dp.message(ReminderStates.waiting_for_time)
async def save_reminder(message: types.Message, state: FSMContext):
    try:
        time = datetime.strptime(message.text, "%H:%M")
        hour = time.hour
        minute = time.minute
    except ValueError:
        await message.answer("❌ Wrong format! Use HH:MM\nExample: 20:00")
        return
    
    user_id = message.from_user.id
    data = await state.get_data()
    timezone = data.get("timezone", "UTC")
    
    if user_id in user_reminders:
        try:
            scheduler.remove_job(f"reminder_{user_id}")
        except:
            pass
    
    user_reminders[user_id] = {
        "hour": hour,
        "minute": minute,
        "timezone": timezone
    }
    scheduler.add_job(
        send_reminder,
        trigger="cron",
        hour=hour,
        minute=minute,
        timezone=timezone,
        id=f"reminder_{user_id}",
        args=[user_id],
        replace_existing=True
    )
    
    await message.answer(
        f"✅ Reminder set!\n"
        f"⏰ Every day at {message.text}\n"
        f"🌍 Timezone: {timezone}",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@dp.message(F.text == "📋 My Reminders")
async def my_reminders(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_reminders:
        await message.answer("No reminders set! 📭", reply_markup=get_reminder_keyboard())
        return
    
    reminder = user_reminders[user_id]
    await message.answer(
        f"🔔 Your reminder:\n"
        f"⏰ Every day at {reminder['hour']:02d}:{reminder['minute']:02d}\n"
        f"🌍 Timezone: {reminder['timezone']}",
        reply_markup=get_reminder_keyboard()
    )

@dp.message(F.text == "🗑️ Delete Reminder")
async def delete_reminder(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_reminders:
        await message.answer("No reminders to delete! 📭", reply_markup=get_reminder_keyboard())
        return
    
    scheduler.remove_job(f"reminder_{user_id}")
    del user_reminders[user_id]
    
    await message.answer(
        "✅ Reminder deleted!",
        reply_markup=get_reminder_keyboard()
    )

async def send_reminder(user_id: int):
    await bot.send_message(
        user_id,
        "🔔 Don't forget to record your expenses today! 💰\n"
        "Press ➕ Add Transaction"
    )

# ══════════════════════════════════════
#            Edit Category
# ══════════════════════════════════════
@dp.message(F.text == "✏️ Edit Categories")
async def edit_categories(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    categories = await get_categories_api(token)
    
    
    text = "📋 Your Custom Categories:\n━━━━━━━━━━━━━━━\n"
    if not categories:
        text += "No custom categories yet!\n"
    else:
        for cat in categories:
            text += f"• {cat['emoji']} {cat['name']}\n"
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Add Category"),
                KeyboardButton(text="🗑️ Delete Category")
            ],
            [KeyboardButton(text="⬅️ Back")]
        ],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=keyboard)

@dp.message(F.text == "➕ Add Category")
async def add_category_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter category name:\nExample: Gym",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CategoryStates.waiting_for_name)

@dp.message(CategoryStates.waiting_for_name)
async def save_category_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Enter emoji for category:\nExample: 💪\n\n"
        "Or press ⏭ Skip for default 📝",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(CategoryStates.waiting_for_emoji)

@dp.message(CategoryStates.waiting_for_emoji)
async def save_category_emoji(message: types.Message, state: FSMContext):
    emoji = "📝" if message.text == "⏭ Skip" else message.text
    data = await state.get_data()
    token = user_tokens.get(message.from_user.id)
    
    result = await add_category_api(token, data.get("name"), emoji)
    
    if "success" in result:
        await message.answer(
            f"✅ Category {emoji} {data.get('name')} added!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())
    
    await state.clear()

# ══════════════════════════════════════
#             Logout
# ══════════════════════════════════════
@dp.message(F.text == "🚪 Logout")
async def logout_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Yes, logout"),
                KeyboardButton(text="❌ No, stay")
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Are you sure you want to logout?",
        reply_markup=keyboard
    )

@dp.message(F.text == "✅ Yes, logout")
async def confirm_logout(message: types.Message, state: FSMContext):
    user_tokens.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(
        "👋 Logged out successfully!",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "❌ No, stay")
async def cancel_logout(message: types.Message):
    await message.answer(
        "❌ Logout cancelled!",
        reply_markup=get_main_keyboard()
    )
# ══════════════════════════════════════
#              HELP
# ═════════════════════════════════════

@dp.message(Command("help"))
@dp.message(F.text == "ℹ️ Help")
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Finance Tracker Help\n━━━━━━━━━━━━━━━━━━━━\n " +
        "📝 Register — create a new account\n" +
        "🔑 Login — login to your account\n" +
        "💰 Balance — view your balance\n" +
        "➕ Add Transaction — add income or expense\n" +
        "📊 History — view your transactions\n" +
        "❌ Cancel — cancel current action\n" +
        "\n━━━━━━━━━━━━━━━━━━━━\n" +
        "💡 Tip: Use the menu buttons below!",
        reply_markup=get_back_keyboard()
    )


# ══════════════════════════════════════
#              MAIN
# ══════════════════════════════════════

async def set_commands():
    commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="profile", description="Show profile"),
        BotCommand(command="help", description="Show help"),
        BotCommand(command="register", description="Register"),
        BotCommand(command="login", description="Login"),
        BotCommand(command="balance", description="Show balance"),
        BotCommand(command="history", description="Transaction history"),
        BotCommand(command="add", description="Add transaction"),
        BotCommand(command="settings", description="Show settings"),
    ]
    await bot.set_my_commands(commands)

async def main():
    scheduler.start()
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())