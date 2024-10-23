from api.logging_config import setup_logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.dependencies import get_current_active_user, get_db
from api.models.mymodel import MymodelModel
from api.schemas import ErrorResponse, SuccessResponse, UserBase
from api.schemas.myschemas import ModelRequest, ModelResponseGetAll, ModelResponseGet
from api.utils.support import exception_handler

router = APIRouter(prefix="/backend/v1/api/mydata", tags=["mydata"])
logger = setup_logging(__name__)

current_user = {"userID": "1", "domain": "admin"} # TODO: get from token


@router.post(
    "",
    response_model=SuccessResponse,
    responses={409: {"model": ErrorResponse}},
)
async def create_remote_media_int(
    data: ModelRequest,
    db: AsyncSession = Depends(get_db),
    #current_user: UserBase = Depends(get_current_active_user),
):
    try:
        model = MymodelModel(current_user["domain"])
        new_item = model(**data.dict())
        new_item.updated_by = current_user["userID"]
        db.add(new_item)
        await db.commit()
        model_orm = ModelResponseGet.from_orm(new_item).dict()
        return model_orm
    except Exception as err:
        logger.error(f"Error occurred creating Data: {err}")
        await db.rollback()
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)


@router.get(
    "/{item_id}",
    response_model=SuccessResponse,
)
async def get_remote_media(
    item_id: UUID4,
    db: AsyncSession = Depends(get_db),
    #current_user: UserBase = Depends(get_current_active_user),
):
    try:
        model = MymodelModel(current_user["domain"])
        item = await model.get(db, id=item_id)
        return SuccessResponse(data= ModelResponseGet.from_orm(item).dict())
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)

@router.get(
    "",
    response_model=SuccessResponse,
)
async def get_remote_media_list(
    db: AsyncSession = Depends(get_db),
    #current_user: UserBase = Depends(get_current_active_user),
):
    try:
        model = MymodelModel(current_user["domain"])
        items = await model.get_all(db)
        return SuccessResponse(data= ModelResponseGetAll.from_orm(items).dict())
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)

@router.put(
    "/{item_id}",
    response_model=SuccessResponse,
)
async def update_remote_media(
    item_id: UUID4,
    data: ModelRequest = None,
    db: AsyncSession = Depends(get_db),
    #current_user: UserBase = Depends(get_current_active_user),
):
    try:
        model = MymodelModel(current_user["domain"])
        item = await model.update(db, id=item_id, updated_by=current_user["userID"], **data.dict())
        return SuccessResponse(data= ModelResponseGet.from_orm(item).dict())
    except Exception as err:
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)


@router.delete(
    "/{item_id}",
    response_model=SuccessResponse,
)
async def delete_remote_media(
    item_id: UUID4,
    db: AsyncSession = Depends(get_db),
    #current_user: UserBase = Depends(get_current_active_user),
):
    try:
        model = MymodelModel(current_user["domain"])
        await model.delete(db, id=item_id, updated_by=current_user["userID"])
        return SuccessResponse(data="Data has been Deleted successfully")
    except Exception as err:
        logger.error(f"Error occurred deleting Data: {err}")
        await db.rollback()
        error, code = exception_handler(err)
        return JSONResponse(content=error, status_code=code)