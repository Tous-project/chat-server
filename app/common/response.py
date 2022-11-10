from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_message: str
    detail: str
