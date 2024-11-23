from typing_extensions import Annotated
from pydantic import BeforeValidator, EmailStr, Field, BaseModel

from ...core.models.model_validators import remove_whitespaces


class Login(BaseModel):
    email: EmailStr
    password: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=8)
    


class SignUp(Login):
    full_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=3)


class AuthSuccess(BaseModel):
    token: str
    refresh_token: str
    
class AuthFailure(BaseModel):
    error: str

class RefreshSuccess(BaseModel):
    token: str