from email.mime import message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime
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

# ══════════════════════════════════════
#              BOT & DISPATCHER
# ══════════════════════════════════════

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_tokens = {}

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
        await message.answer(
            "Registration successful! 🎉",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    else:
        await message.answer(
            f"Registration failed: {result.get('detail', 'Unknown error')}",
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
            await message.answer(
                "Registration successful! 🎉",
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
    await message.answer(
        "Choose category:",
        reply_markup=get_category_keyboard()
    )
    await state.set_state(AddTransactionStates.waiting_for_category)

@dp.message(
    F.text.in_(["🍔 Food", "💼 Salary", "🚗 Transport", "🏠 Housing", "🎮 Entertainment", "📝 Other"]),
    AddTransactionStates.waiting_for_category
)
async def add_transaction_category(message: types.Message, state: FSMContext):
    category = message.text.split(" ", 1)[1].lower()  # "🍔 Food" → "food"
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
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())