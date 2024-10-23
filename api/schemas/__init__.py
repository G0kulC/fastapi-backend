# Default Responses
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    ok: bool = True
    data: dict | list | str | None = None


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str


class UserBase(BaseModel):
    email: str
    role: str


# Authentication and Authorization
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class TokenData(BaseModel):
    username: str | None = None


class ExceptionSchema:
    def __init__(self):
        self.error_messages = {
            "Database is not up to date": [
                "Database is not up to date. Please update the database",
                400,
            ],
            "not found": ["Data not found", 404],
            "unique constraint": ["Data already exists", 409],
            "psycopg2.errors.undefinedcolumn": [
                "Some of the column is missing in the table. Please ensure that all migrations are applied to update the database schema to the latest version.",
                400,
            ],
        }

    def get_error_message(self, error_type):
        for key, value in self.error_messages.items():
            if key.lower() in str(error_type):
                return value[0], value[1]
        return f"An unexpected error occurred.Please try again later", 500
