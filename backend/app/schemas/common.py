from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
