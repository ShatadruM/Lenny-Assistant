from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy import text
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.db.session import engine
from app.db.models import Base

app = FastAPI(title="The Lenny Growth Assistant API")

# Allow requests from the frontend (read from env or default to localhost)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Initialize tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Handle schema updates for existing databases
        await conn.execute(text("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_id VARCHAR;"))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")