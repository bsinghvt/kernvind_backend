import logging
from typing import Any
from quart_schema import validate_headers, validate_request, validate_response

from ..models.api_models import AuthFailure, AuthSuccess, Login, RefreshSuccess
from ..services.user_auth_service import user_login

from ...core.models.headers_model import Headers


from quart_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity,
    create_access_token,
    get_jwt_claims,
)
from quart import Blueprint


login_bp = Blueprint('login', __name__)

@login_bp.post('/login')
@validate_request(Login)
@validate_response(AuthSuccess, 200)
@validate_response(AuthFailure, 401)
@validate_response(AuthFailure, 500)
async def login_user(data: Login)->Any:
    resp =  await user_login(login=data)
    return resp

@login_bp.post('/refresh')
@validate_headers(Headers)
@validate_response(RefreshSuccess, 200)
@validate_response(AuthFailure, 401)
@validate_response(AuthFailure, 500)
@jwt_refresh_token_required
async def refresh_user_token(headers: Headers)->Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    access_token = create_access_token(identity=current_user, user_claims=user_claims)
    logging.info(access_token)
    return RefreshSuccess(token=access_token)

@login_bp.get('/health')
async def health_check()->Any:
    return 'ok'