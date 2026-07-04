from pydantic import BaseModel, Field

class ErrorResponseSchema(BaseModel):
    error: str = Field(..., description="The exact exception class name", examples=["ErrorClassName"])
    detail: str = Field(..., description="Human-readable error message", examples=["Human readable explanation of why it failed."])
    meta: dict = Field(default_factory=dict, description="Additional context about the error", examples=[{"key": "value"}])
