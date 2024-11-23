
from pydantic import BaseModel


class Failure(BaseModel):
    error: str