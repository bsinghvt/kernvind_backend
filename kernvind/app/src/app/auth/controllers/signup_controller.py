from typing import Any
from quart_schema import validate_request, validate_response

from ..models.api_models import AuthFailure, AuthSuccess, SignUp
from ..services.user_auth_service import user_signup
from quart import Blueprint


signup_bp = Blueprint('signup', __name__)


@signup_bp.post('/signup')
@validate_request(SignUp)
@validate_response(AuthSuccess, 201)
@validate_response(AuthFailure, 401)
@validate_response(AuthFailure, 409)
@validate_response(AuthFailure, 500)
async def signup_user(data: SignUp) -> Any:
    resp =  await user_signup(sign_up=data)
    return resp
    