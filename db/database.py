import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Ensure the .db file is stored in a directory that can be mounted as a Docker volume
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Path to the shared SQLite database
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'kitchen.db')}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory for dependent injection
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables (Models defined in db.models)
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency injection method for FastAPI."""
    async with async_session() as session:
        yield session
