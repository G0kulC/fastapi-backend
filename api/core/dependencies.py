import json
from api.logging_config import setup_logging
from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from api.schemas import UserBase
from api.utils import JsonException

logger = setup_logging(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db(request: Request):
    return request.state.db


server_error = JsonException(
    detail={
        "status": False,
        "error": "An unexpected error occurred.Please try again later",
    },
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    headers={"WWW-Authenticate": "Bearer", "Content-Type": "application/json"},
)


def validate_session(token, method, url_parts):

    try:
        pass
    except JsonException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise server_error


def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None):
    try:
        pass
    except JsonException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise server_error


async def get_current_active_user(current_user: UserBase = Depends(get_current_user)):
    return current_user["data"]
