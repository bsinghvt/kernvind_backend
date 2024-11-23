from pydantic import BaseModel


class UserClaims(BaseModel):
    full_name: str
    
class Jwt(BaseModel):
    iat: int
    nbf: int
    jti: str
    exp: int
    identity: int
    fresh: bool
    type: str
    user_claims: UserClaims