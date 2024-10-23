import json
import asyncio
import aiohttp
from sqlalchemy import UUID
from api.logging_config import setup_logging
from datetime import datetime as dt
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from api.schemas import ErrorResponse, ExceptionSchema

logger = setup_logging(__name__)

def exception_handler(err):
    try:
        now = dt.now()
        raised_err = str(err).lower()
        logger.info(f"Error raised exception_handler: {raised_err} - {now}")
        exception_schema = ExceptionSchema()
        error_response = ErrorResponse(
            error="An unexpected error occurred.Please try again later"
        )
        code = 500
        error_response.error, code = exception_schema.get_error_message(raised_err)
        if "pricebook item" in error_response.error.lower():
            error_response.error = raised_err
        if "you cannot delete this design" in error_response.error.lower():
            error_response.error = str(err)
        content = error_response.dict()
        return content, code
    except Exception as e:
        logger.error(f"Error occurred error handler - {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred.Please try again later",
                "status": False,
            },
        )
