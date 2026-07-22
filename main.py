from fastapi import FastAPI
from Routers.auth import router as auth_router
from Database.db import setup_database
from Routers.transactions import router as transactions_router
from Routers.categories import router as categories_router
from Routers.goals import router as goals_router

app = FastAPI()
app.include_router(transactions_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(goals_router)

@app.on_event("startup")
async def on_startup():
    await setup_database()