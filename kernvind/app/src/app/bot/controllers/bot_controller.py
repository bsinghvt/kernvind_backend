
import logging
from typing import Any, List
from ..models.bot_llm_change_model import BotChangeLlm
from ..services.bot_change_llm_service import bot_change_llm
from quart import Blueprint
from quart_schema import  validate_headers, validate_request, validate_response
from quart import Blueprint

from ..services.bot_remove_user_service import bot_remove_user

from ..services.bot_remove_datasource_service import bot_remove_datasource

from ..services.bot_delete_service import bot_delete

from ..services.bot_add_user_service import bot_add_user

from ..models.bot_add_user_model import BotAddUser

from ..services.bot_update_name_desc_service import bot_update_name_desc

from ..models.bot_update_name_desc_model import BotUpdateNameDescIn

from ..services.get_bot_details_service import get_bot_details

from ..models.bot_details_model import BotDetails

from ..models.bot_add_datasource_model import BotAddDataSource

from ...core.models.user_claims_model import UserClaims
from ...core.models.headers_model import Headers
from ...core.models.error_model import Failure

from ..services.get_bot_messages_service import get_bot_messages
from ..models.get_bot_list_model import GetBot
from ..services.get_bot_list import bot_list
from ..services.bot_add_datasource_service import bot_add_datasource
from ..models.chat_message_model import ChatMessageOut
from ..services.create_bot import create_bot
from ..models.new_bot_models import  BotIn, BotOut
from ...core.models.success_model import Success

from quart_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)


bot_bp = Blueprint('bot', __name__)


@bot_bp.get('/messages/<bot_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(List[ChatMessageOut], 200)
@validate_response(Failure, 401)
@validate_response(Failure, 400)
@validate_response(Failure, 500)
async def bot_get_messages(bot_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    bot_id_int: int
    try:
        bot_id_int = int(bot_id)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Bad request"), 400
    return await get_bot_messages(bot_id=bot_id_int, user_id=current_user)

@bot_bp.get('/list')
@validate_response(List[GetBot], 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def list_bot(headers: Headers) -> Any:
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

    resp = await bot_list(current_user)
    return resp

@bot_bp.get('/details/<bot_id>')
@validate_response(BotDetails, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def bot_details(headers: Headers, bot_id: str) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    bot_id_int: int
    try:
        bot_id_int = int(bot_id)
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401

    resp = await get_bot_details(bot_id=bot_id_int, user_id=current_user)
    return resp

@bot_bp.post('/create')
@jwt_required
@validate_headers(Headers)
@validate_request(BotIn)
@validate_response(BotOut, 201)
@validate_response(Failure, 409)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def bot_create(data: BotIn, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if full_name != data.created_by_name:
        return Failure(error="unauthenticated"), 401
    if data.created_by_user_id != current_user:
        return Failure(error="unauthenticated"), 401

    resp = await create_bot(bot_in=data)
    return resp

@bot_bp.put('/llm')
@jwt_required
@validate_headers(Headers)
@validate_request(BotChangeLlm)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def change_bot_llm(data: BotChangeLlm, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    

    resp = await bot_change_llm(user_id=current_user,
                                    bot_id=data.bot_id, 
                                    user_llm_id=data.user_llm_id)
    return resp

@bot_bp.put('/datasource')
@jwt_required
@validate_headers(Headers)
@validate_request(BotAddDataSource)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def bot_datasource(data: BotAddDataSource, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    

    resp = await bot_add_datasource(user_id=current_user,
                                    bot_id=data.bot_id, 
                                    datasource_id=data.datasource_id)
    return resp

@bot_bp.put('/update')
@jwt_required
@validate_headers(Headers)
@validate_request(BotUpdateNameDescIn)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def update_bot_name_desc(data: BotUpdateNameDescIn, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    

    resp = await bot_update_name_desc(bot_in=data, user_id=current_user)
    return resp

@bot_bp.put('/adduser')
@jwt_required
@validate_headers(Headers)
@validate_request(BotAddUser)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def add_bot_user(data: BotAddUser, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    

    resp = await bot_add_user(bot_new_user=data, user_id=current_user)
    return resp

@bot_bp.delete('/delete/<bot_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(Success, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def delete_bot(bot_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    bot_id_int: int
    try:
        bot_id_int = int(bot_id)
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    

    resp = await bot_delete(bot_id=bot_id_int, user_id=current_user)
    return resp

@bot_bp.delete('/datasource/<bot_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def remove_bot_datasource(bot_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    bot_id_int: int
    try:
        bot_id_int = int(bot_id)
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user is unauthenticated"), 401
    

    resp = await bot_remove_datasource(bot_id=bot_id_int, user_id=current_user)
    return resp

@bot_bp.delete('user/<bot_id>/<remove_user_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(BotDetails, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def remove_bot_user(bot_id: str, remove_user_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    bot_id_int: int
    remove_user_id_int: int
    try:
        remove_user_id_int = int(remove_user_id)
        bot_id_int = int(bot_id)
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user is unauthenticated"), 401
    

    resp = await bot_remove_user(bot_id=bot_id_int, user_id=current_user, remove_user_id=remove_user_id_int, token=headers.authorization)

    return resp