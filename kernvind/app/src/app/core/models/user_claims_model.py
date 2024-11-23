from pydantic import BaseModel


class UserClaims(BaseModel):
    full_name: str