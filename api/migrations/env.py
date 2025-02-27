from logging.config import fileConfig
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, engine_from_config
from sqlalchemy import pool

from alembic import context

from api.logging_config import setup_logging
logger = setup_logging(__name__)

ENV_NAME = os.environ.get("ENV_NAME", "dev")
ENV_FILE = f"{os.path.join(os.getcwd(), ENV_NAME)}.env"

if os.path.exists(ENV_FILE):
    logger.info("Loading env file from %s", ENV_FILE)
    load_dotenv(ENV_FILE)
else:
    logger.info("No %s.env file found. Relying on system env", ENV_NAME)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = Model("public").metadata

target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_NAME = os.environ.get("DB_NAME", "")
DB_UNAME = os.environ.get("DB_UNAME", "")
DB_PWORD = os.environ.get("DB_PWORD", "")
DB_URL = f"postgresql://{DB_UNAME}:{DB_PWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


version_table_schema = config.get_main_option("version_table_schema")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=DB_URL,
        version_table_schema=version_table_schema,
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
    connectable = create_engine(DB_URL, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            version_table_schema=version_table_schema,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

