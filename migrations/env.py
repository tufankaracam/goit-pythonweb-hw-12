import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

# Alembic Config nesnesi, .ini dosyasındaki değerleri sağlar.
config = context.config

# Python logging yapılandırmasını ayarla.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy modellerini içe aktar ve metadata'yı ayarla.
from src.database.models import Base

target_metadata = Base.metadata

# Asenkron migration işlemlerini çalıştıracak fonksiyonlar.


def run_migrations_offline() -> None:
    """Migrationları 'offline' modda çalıştır."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Migrationları 'online' modda çalıştır."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Migration işlemini gerçekleştir."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
