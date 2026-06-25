# Finance Tracker 💰

A personal finance tracking application with a **Telegram Bot** interface, built with **FastAPI** and **SQLite**.

Track your income and expenses, view your balance, and manage transactions — all from Telegram!

---

## ✨ Features

- 📝 **Register & Login** — secure authentication with JWT tokens
- 💰 **Add Transactions** — income and expense tracking with categories
- 📊 **View Balance** — real-time balance with income/expense breakdown
- 📋 **Transaction History** — formatted list of all your transactions
- 🔐 **JWT Authentication** — secure token-based auth
- ✅ **Input Validation** — phone, password, amount, date validation
- 🎯 **Inline Keyboards** — easy category and type selection

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Programming language |
| **FastAPI** | REST API backend |
| **SQLAlchemy** | ORM (async) |
| **SQLite** | Database |
| **aiogram 3.x** | Telegram Bot |
| **JWT (python-jose)** | Authentication |
| **Pydantic** | Data validation |
| **passlib + bcrypt** | Password hashing |
| **httpx** | Async HTTP client |
| **python-dotenv** | Environment variables |

---

## 📁 Project Structure

```
Finance_Tracker/
│
├── Database/
│   └── db.py                 # Database connection and session
│
├── Models/
│   └── models.py             # SQLAlchemy models (ProfileModel, TransactionModel)
│
├── Schemas/
│   └── schemas.py            # Pydantic schemas for request/response
│
├── Routers/
│   ├── auth.py               # Register and login endpoints
│   └── transactions.py       # Transaction CRUD endpoints
│
├── Core/
│   └── security.py           # JWT tokens, password hashing, get_current_user
│
├── Bot/
│   └── bot.py                # Telegram bot with all commands
│
├── .env                      # Environment variables (not in git!)
├── .gitignore                # Git ignore file
├── main.py                   # FastAPI app entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kostiantyn-Shtoiko/Finance_Tracker.git
cd Finance_Tracker
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```bash
# .env
SECRET_KEY=your_super_secret_key_here
BOT_TOKEN=your_telegram_bot_token_here
```

> Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram

---

## 🚀 Usage

### Run FastAPI server

```bash
uvicorn main:app --reload
```

### Run Telegram Bot (in a separate terminal)

```bash
python Bot/bot.py
```

> ⚠️ Both must run at the same time!

---

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/register` | Create a new account |
| `/login` | Login to your account |
| `/balance` | View your current balance |
| `/add` | Add a new transaction |
| `/history` | View transaction history |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login and get JWT token |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/transactions/` | Add new transaction |
| `GET` | `/transactions/` | Get all transactions |
| `GET` | `/transactions/balance` | Get balance summary |
| `DELETE` | `/transactions/{id}` | Delete a transaction |

> 📖 Full API documentation available at `http://localhost:8000/docs`

---

## 🔐 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | JWT secret key | `a3f8c2d1e4b5...` |
| `BOT_TOKEN` | Telegram bot token | `1234567890:ABC...` |

---

## 📱 Bot Preview

```
💰 Your Finance Summary
━━━━━━━━━━━━━━━
📈 Income:  +5000.00
📉 Expense: -1500.00
━━━━━━━━━━━━━━━
💵 Balance:  3500.00


📊 Your Transaction History:
━━━━━━━━━━━━━━━━━━━━
1. 📈 Salary
   📁 salary | 💵 5000.00
   📅 2024-01-15

2. 📉 Lunch
   📁 food | 💵 150.00
   📅 2024-01-15
━━━━━━━━━━━━━━━━━━━━
Total: 2 transactions
```
## 🚀 Live Demo
- API: https://financetracker-production-d18b.up.railway.app
- Bot: @твій_бот_username
- Docs: https://financetracker-production-d18b.up.railway.app/docs
  
---

## 👨‍💻 Author

**Kostiantyn Shtoiko**
- GitHub: [@Kostiantyn-Shtoiko](https://github.com/Kostiantyn-Shtoiko)

---

## 📄 License

MIT License — feel free to use this project!
