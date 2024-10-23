from pydantic import UUID4, BaseModel
from api.schemas import SuccessResponse

class ModelRequest(BaseModel):
    column: str
    # rest of columns

class ModelOrm(ModelRequest):
    id: UUID4

    class Config:
        orm_mode = True


class ModelResponseGet(SuccessResponse):
    data: ModelOrm

class ModelResponseGetAll(SuccessResponse):
    data: list[ModelOrm]
