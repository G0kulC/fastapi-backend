import logging
import os
from dotenv import load_dotenv

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG")
DB_LOGLEVEL = os.environ.get("DB_LOGLEVEL", "INFO")

logging.basicConfig(
    level=LOGLEVEL,
    format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ENV_NAME = os.environ.get("ENV_NAME", "dev")
ENV_FILE = f"{os.path.join(os.getcwd(), ENV_NAME)}.env"

if os.path.exists(ENV_FILE):
    logger.info("Loading env file from %s", ENV_FILE)
    load_dotenv(ENV_FILE)
else:
    logger.info("No %s.env file found. Relying on system env", ENV_NAME)

DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_NAME = os.environ.get("DB_NAME", "")
DB_UNAME = os.environ.get("DB_UNAME", "")
DB_PWORD = os.environ.get("DB_PWORD", "")
DB_POOL_SIZE = os.environ.get("DB_POOL_SIZE", 10)
DB_MAX_OVERFLOW = os.environ.get("DB_MAX_OVERFLOW", 30)
AUTH_SERVICE_HOST = os.environ.get("AUTH_SERVICE_HOST", "http://0.0.0.0")
AUTH_SERVICE_PORT = os.environ.get("AUTH_SERVICE_PORT", "8080")

