from typing import Any

from quart_schema import  validate_request, validate_response

from ..services.google_sign_in_service import user_google_login

from ..models.google_sign_in_model import GoogleSigIn

from ..models.api_models import AuthFailure, AuthSuccess

from quart import Blueprint


social_auth_bp = Blueprint('social_auth', __name__)


@social_auth_bp.post('/googlesignin')
@validate_request(GoogleSigIn)
@validate_response(AuthSuccess, 200)
@validate_response(AuthSuccess, 201)
@validate_response(AuthFailure, 400)
@validate_response(AuthFailure, 401)
@validate_response(AuthFailure, 500)
async def google_sign_in(data: GoogleSigIn)->Any:
    resp =  await user_google_login(login=data)
    return resp