from pydantic import BaseModel


class RefreshTokenInternal(BaseModel):
    user_id: int
    token: str
