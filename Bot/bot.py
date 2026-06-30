from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://financetracker-production-d18b.up.railway.app")

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

class AddTransactionStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_date = State()

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
                KeyboardButton(text="📊 History")
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
#              LOGIN
# ══════════════════════════════════════

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
        await message.answer("Logged in! ✅", reply_markup=get_main_keyboard())
    else:
        await message.answer("Wrong phone or password! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#              REGISTER
# ══════════════════════════════════════

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
    if len(message.text) < 6:
        await message.answer("❌ Password too short! Minimum 6 characters!")
        return
    if len(message.text) > 120:
        await message.answer("❌ Password too long! Maximum 120 characters!")
        return

    await state.update_data(password=message.text)
    data = await state.get_data()

    result = await register_user(
        data.get("last_name"),
        data.get("first_name"),
        data.get("phone"),
        data.get("password")
    )

    if "success" in result:
        await message.answer("Registration complete! ✅", reply_markup=get_main_keyboard())
    else:
        await message.answer("Registration failed! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#              BALANCE
# ══════════════════════════════════════

@dp.message(F.text == "💰 Balance")
async def balance_command(message: types.Message):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("Please login first! 🔑")
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

@dp.message(F.text == "📊 History")
async def history_command(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("Please login first! 🔑")
        return

    transactions = await get_transactions(token)
    if not transactions:
        await message.answer("No transactions found 📭", reply_markup=get_main_keyboard())
        return
    
    await state.update_data(transactions=transactions, page=0)
    await show_history_page(message, transactions, page=0)

async def show_history_page(message_or_callback, transactions, page):
    total_pages = (len(transactions) - 1) // ITEMS_PER_PAGE + 1
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_transactions = transactions[start:end]
    
    text = f"📊 History (Page {page + 1}/{total_pages})\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    
    for i, tx in enumerate(page_transactions, start + 1):
        emoji = "📈" if tx['type'] == "income" else "📉"
        text += f"{i}. {emoji} {tx['title']} | {tx['amount']:.2f}\n"

    keyboard_rows = []
    for tx in page_transactions:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"🗑️ Delete: {tx['title']}", 
                callback_data=f"delete_{tx['id']}"
            )
    ])

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="▶️ Next", callback_data=f"page_{page+1}"))
    
    if buttons:
        keyboard_rows.append(buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows) if keyboard_rows else None

    if isinstance(message_or_callback, types.CallbackQuery):
        await message_or_callback.message.answer(text, reply_markup=keyboard)
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)

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

@dp.message(F.text == "➕ Add Transaction")
async def add_transaction_start(message: types.Message, state: FSMContext):
    token = user_tokens.get(message.from_user.id)
    if not token:
        await message.answer("Please login first! 🔑")
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
        "Please enter the title:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddTransactionStates.waiting_for_title)

@dp.message(AddTransactionStates.waiting_for_title)
async def add_transaction_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Please enter the date (YYYY-MM-DD):\nExample: 2024-01-15")
    await state.set_state(AddTransactionStates.waiting_for_date)

@dp.message(AddTransactionStates.waiting_for_date)
async def add_transaction_date(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Wrong format! Use: YYYY-MM-DD\nExample: 2024-01-15")
        return

    await state.update_data(date=message.text)
    data = await state.get_data()
    token = user_tokens.get(message.from_user.id)

    result = await add_transaction(token, data)

    if "success" in result:
        await message.answer("Transaction added! ✅", reply_markup=get_main_keyboard())
    else:
        await message.answer("Something went wrong! ❌", reply_markup=get_main_keyboard())

    await state.clear()

# ══════════════════════════════════════
#              MAIN
# ══════════════════════════════════════

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())