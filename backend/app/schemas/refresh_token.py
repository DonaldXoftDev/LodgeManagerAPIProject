from pydantic import BaseModel, Field


class RefreshTokenInternal(BaseModel):
    user_id: int = Field(..., description="The ID of the user.", examples=[1])
    token: str = Field(..., description="The refresh token string.", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
