from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.db.session import engine
from app.db.models import Base

app = FastAPI(title="The Lenny Growth Assistant API")

# Allow requests from the React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Initialize tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(chat_router, prefix="/api")