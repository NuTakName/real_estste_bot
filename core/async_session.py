from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    url=settings["db"]["url"],
    pool_use_lifo=True,
)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

