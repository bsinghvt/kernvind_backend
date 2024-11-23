
import logging
from typing import Any, List

from ..services.delete_user_llm_service import delete_user_llm
from ...core.models.success_model import Success
from quart import Blueprint
from quart_schema import  validate_headers, validate_request, validate_response
from quart import Blueprint
from quart_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)

from ..services.update_user_llm_service import update_user_llm

from ..models.user_llm_update_model import UserLlmUpdateIn

from ..models.user_llm_details_model import UserLlmDetails

from ..services.get_user_llm_details_service import get_user_llm_details_service

from ..services.get_user_llm_list_service import get_user_llm_list_service
from ..services.create_user_llm_service import create_user_llm_service

from ...core.models.user_claims_model import UserClaims
from ...core.models.error_model import Failure
from ...core.models.headers_model import Headers

from ..models.user_llm_model import  UserLlmIn, UserLlmOut


user_llm_bp = Blueprint('user_llm', __name__)

@user_llm_bp.get('/list')
@validate_response(List[UserLlmOut], 200)
@validate_response(Failure, 500)
@jwt_required
@validate_headers(Headers)
async def user_llm_list_route(headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    

    return await get_user_llm_list_service(current_user)

@user_llm_bp.post('/create')
@jwt_required
@validate_headers(Headers)
@validate_request(UserLlmIn)
@validate_response(UserLlmOut, 201)
@validate_response(Failure, 409)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
@validate_response(Failure, 400)
async def user_llm_create_route(data: UserLlmIn, headers: Headers) -> Any:
    current_user = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    full_name = user_claims_obj.full_name
    if not full_name or data.user_id != current_user:
        return Failure(error="current user unauthenticated"), 401
    resp = await create_user_llm_service(user_llm_in=data)
    return resp

@user_llm_bp.put('/update')
@jwt_required
@validate_headers(Headers)
@validate_request(UserLlmUpdateIn)
@validate_response(UserLlmDetails, 200)
@validate_response(Failure, 409)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
@validate_response(Failure, 400)
async def user_llm_update_route(data: UserLlmUpdateIn, headers: Headers) -> Any:
    current_user = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    full_name = user_claims_obj.full_name
    if not full_name or data.user_id != current_user:
        return Failure(error="current user unauthenticated"), 401
    resp = await update_user_llm(user_llm_update_in=data)
    return resp


@user_llm_bp.get('/details/<user_llm_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(UserLlmDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def user_llm_get_details(user_llm_id: str, headers: Headers) -> Any:
    current_user = get_jwt_identity()
    user_claims = get_jwt_claims()
    user_llm_id_int: int
    try:
        user_llm_id_int = int(user_llm_id)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Not a valid request"), 400
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401

    resp = await get_user_llm_details_service(user_id=current_user, user_llm_id=user_llm_id_int)
    return resp

@user_llm_bp.delete('/delete/<user_llm_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(Success, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 400)
@validate_response(Failure, 500)
async def user_llm_delete(user_llm_id: str, headers: Headers) -> Any:
    current_user = get_jwt_identity()
    user_claims = get_jwt_claims()
    user_llm_id_int: int
    try:
        user_llm_id_int = int(user_llm_id)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Not a valid request"), 400
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401

    resp = await delete_user_llm(user_id=current_user, user_llm_id=user_llm_id_int)
    return resp