from fastapi import APIRouter

from api.routers import (
    myrouter,
)

router = APIRouter()
router.include_router(myrouter.router)

