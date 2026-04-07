from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config.settings import settings

engine: AsyncEngine = create_async_engine(
    settings.postgres_async_connection,
    echo=settings.sqlalchemy_echo,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()