import os
from api.logging_config import setup_logging
from alembic import op
from sqlalchemy import inspect
from datetime import datetime as dt
from alembic import command
from alembic.config import Config

from api import DB_HOST, DB_NAME, DB_PORT, DB_PWORD, DB_UNAME

DB_URL = f"postgresql://{DB_UNAME}:{DB_PWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
REVESIONS_DIR = os.path.dirname(os.path.realpath(__file__))
alembic_cfg = Config()
logger = setup_logging(__name__)


def enable_feature(schema: str):
    try:
        logger.info(f"Enabling feature for the tenant - {schema} on {REVESIONS_DIR}")
        alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)
        alembic_cfg.set_main_option("schema_name", schema)
        alembic_cfg.set_main_option("script_location", REVESIONS_DIR)
        alembic_cfg.set_main_option("version_table_schema", schema)
        return command.upgrade(alembic_cfg, "heads")
    except Exception as e:
        logger.exception(str(e))
        return False


def disable_feature(schema: str):
    try:
        alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)
        alembic_cfg.set_main_option("schema_name", schema)
        alembic_cfg.set_main_option("script_location", REVESIONS_DIR)
        alembic_cfg.set_main_option("version_table_schema", schema)
        return command.downgrade(alembic_cfg, "base")
    except Exception as e:
        logger.exception(str(e))
        return False


# alembic revision --autogenerate -m "my_migration_name"

def alembic_revision(schema: str, message: str):
    try:
        alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)
        alembic_cfg.set_main_option("script_location", REVESIONS_DIR)
        alembic_cfg.set_main_option("version_table_schema", schema)
        return command.revision(alembic_cfg, message, autogenerate=True)
    except Exception as e:
        logger.error(str(e))
        if "Target database is not up to dat" in str(e):
            raise Exception("Database is not up to date. Please update the database")
        return False


def table_exists(table_name, schema_name):
    try:
        inspector = inspect(op.get_bind())
        return inspector.has_table(table_name, schema=schema_name)
    except Exception as e:
        logger.exception(str(e))
        return False


def custom_downgrade(table_name, schema_name):
    try:
        if table_exists(table_name, schema_name):
            op.rename_table(
                table_name,
                f"{table_name}_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}",
                schema=schema_name,
            )
            logger.info(f"downgrade table: {schema_name}.{table_name} is {True}")
            return True
        else:
            return False
    except Exception as e:
        logger.exception(str(e))
        return False
