# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 1. Try Railway's full URL first
DATABASE_URL = os.getenv("MYSQL_URL")

"""
# 2. Fallback to manual build (for local dev)
if not DATABASE_URL:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASS", "")
    db = os.getenv("DB_NAME", "countries_db")
    DATABASE_URL = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}"
"""

if not DATABASE_URL:
    raise RuntimeError("No database connection configured")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
