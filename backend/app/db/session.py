from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Ensure SQLAlchemy uses the asyncpg driver
raw_url = settings.DATABASE_URL
if raw_url and raw_url.startswith("postgresql://"):
    db_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    db_url = raw_url

# Supabase requires SSL. If using Supabase and SSL is not in the URL, append it.
if "supabase" in db_url and "ssl=" not in db_url.lower() and "sslmode=" not in db_url.lower():
    db_url += "?ssl=require" if "?" not in db_url else "&ssl=require"

engine = create_async_engine(
    db_url, 
    echo=False,
    pool_pre_ping=True,  # Pings the DB to check if connection is alive
    pool_recycle=1800,   # Refreshes connections every 30 minutes
    pool_size=5,         # Keeps a small, manageable pool of active connections
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session