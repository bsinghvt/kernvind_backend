from pydantic import BaseModel


class PlaygroundJwt(BaseModel):
    iat: int
    nbf: int
    jti: str
    exp: int
    identity: str
    fresh: bool
    type: str