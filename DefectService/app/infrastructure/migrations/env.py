# migrations/env.py

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.session import Base
from infrastructure.database.models import RoadDefectModel
from core.config.settings import settings

# Конфигурация Alembic
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем URL из настроек
config.set_main_option("sqlalchemy.url", settings.postgres_async_connection)

# Метаданные моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполнение миграций с переданным соединением"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запуск миграций в асинхронном режиме"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме (с подключением к БД)"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()