from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Ensure SQLAlchemy uses the asyncpg driver
raw_url = settings.DATABASE_URL
if raw_url and raw_url.startswith("postgresql://"):
    db_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    db_url = raw_url

engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session