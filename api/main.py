import version as proj_version
from api.logging_config import setup_logging
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.dependencies import get_current_active_user, get_db
from api.migrations import alembic_revision, disable_feature, enable_feature
from api.models import SessionLocal
from api.routers import router
from api.schemas import ErrorResponse, SuccessResponse, UserBase
from api.utils import JsonException
from api.utils.support import (
    exception_handler,
)
from fastapi.exceptions import RequestValidationError

logger = setup_logging(__name__)

origins = ["*"]

# Uncomment below to disable swagger and oauth2-redirect urls
# app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
app = FastAPI(
    docs_url=None,
    openapi_url=None,
    swagger_ui_oauth2_redirect_url=None,
    redoc_url=None,
)
app.include_router(router=router)
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(RequestValidationError)
def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    loc = first_error.get("loc", [])
    field_name = loc[-1] if loc else "unknown field"
    error_msg = first_error.get("msg", "Invalid input")
    if field_name != "unknown field" and type(field_name) == str:
        field_name = field_name.replace("_", " ").capitalize()
    msg = f"Error in field '{field_name}': {error_msg}"
    if "field required" in error_msg:
        msg = f"Field '{field_name}' is required"
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error=msg).dict(),
    )

@app.exception_handler(JsonException)
def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
        headers=exc.headers,
    )

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):

    try:
        async with SessionLocal() as session:
            request.state.db = session
            response = await call_next(request)

    except Exception as e:
        logger.error(f"Error in db_session_middleware: {e}")
        response = JSONResponse(
            content={
                "status": False,
                "error": "An unexpected error occurred. Please try again later.",
            },
            status_code=500,
        )
    finally:
        if hasattr(request.state, "db"):
            await request.state.db.close()
    return response


logger.info("Loading routes...")
for route in app.routes:
    logger.info(f"loading route - {route.methods} {route.path}")

current_user = {"userID": "1", "domain": "admin"} # TODO: get from token

@app.post(
    "/pkg/v1/api/feature",
    response_model=SuccessResponse,
    responses={500: {"model": ErrorResponse}},
)
async def enable_service_feature(
    db: AsyncSession = Depends(get_db),
    # current_user: UserBase = Depends(get_current_active_user),
):
    try:
        schema = current_user["domain"]
        enable_feature(schema=schema)
        logger.info(f"Enabled packaging feature for {schema}")
        return SuccessResponse(data=f"Enabled packaging feature for {schema}")
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)


@app.delete(
    "/pkg/v1/api/feature",
    response_model=SuccessResponse,
    responses={500: {"model": ErrorResponse}},
)
async def disable_service_feature(
    db: AsyncSession = Depends(get_db),
    # current_user: UserBase = Depends(get_current_active_user),
):
    try:
        schema = current_user["domain"]
        disable_feature(schema=schema)
        logger.info(f"Disabled packaging feature for {schema}")
        return SuccessResponse(data=f"Disabled packaging feature for {schema}")
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)


@app.post("/pkg/v1/api/feature/alembic_revision")
async def add_alembic_revision(
    db: AsyncSession = Depends(get_db),
    # current_user: UserBase = Depends(get_current_active_user),
):
    try:
        schema = current_user["domain"]
        alembic_revision(schema=schema,message="Migration Message")
        logger.info(f"alembic revision for {schema}")
        return SuccessResponse(data=f"alembic revision for {schema}")
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)

@app.get("/healthcheck")
async def healthcheck():
    version = proj_version.__version__
    return SuccessResponse(data=f"Core API is up and running. Version: {version}")
