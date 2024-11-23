from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel

from ...core.models.model_validators import remove_whitespaces

class GoogleSigIn(BaseModel):
    id_token: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=1)
    platform: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=3)
    
"""   
class GoogleSignInIdToken(BaseModel):
    iss: str
    azp: str
    aud: str
    sub: int
    email: str
    email_verified: bool
    nonce: str | None | int = None
    nbf: int
    name: str
    picture: str
    given_name: str
    family_name: str
    iat: int
    exp: int
    jti: str
"""

class GoogleSignInIdToken(BaseModel):
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str