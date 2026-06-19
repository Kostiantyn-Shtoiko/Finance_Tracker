from fastapi import FastAPI
from Routers.auth import router as auth_router
from Database.db import setup_database

app = FastAPI()

app.include_router(auth_router)

@app.on_event("startup")
async def on_startup():
    await setup_database()