from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, URL

from alembic import context
from environs import Env

# Step 1: import models:
# Import Syntax: from package.file import class1, class2..
from lesson2_structured.database.models.base import Base

# Import syntax: from package(directory) import module (file)
from lesson2_structured import orders, products, users, order_products

# Step 2: instantiate environment variables
env = Env()
env.read_env('.env')

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Step 3: SET URL
#########
url = URL.create(
    drivername="postgresql+psycopg2",
    username=env.str("POSTGRES_USER"),
    password=env.str("POSTGRES_PASSWORD"),
    host=env.str("DATABASE_HOST"),
    port=5432,
    database=env.str("POSTGRES_DB"),
).render_as_string(hide_password=False)

config.set_main_option(
    "sqlalchemy.url", 
    url)

# Step 4: add your model's MetaData object here
# Note: Has reference to all inherited classes: for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
