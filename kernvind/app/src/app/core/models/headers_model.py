from pydantic import BaseModel


class Headers(BaseModel):
    authorization: str