import asyncio
from datetime import datetime
import logging
from typing import Any, List, Optional
import uuid

from ..services.get_bot_messages_service import get_bot_messages
from ..services.save_message_service import save_message
from langchain_core.language_models.chat_models import BaseChatModel
from ..services.get_bot_datasource_service import get_bot_datasource

from ...core.models.success_model import Success

from ...core.models.headers_model import Headers
from quart_schema import validate_headers, validate_response

from ...core.models.error_model import Failure
from ..model.bot_user_llm_model import BotUserLlm
from ..services.get_pgvector_instance_service import get_pgvector_instance

from ..services.get_lc_llm_service import get_lc_llm

from ..services.get_bot_userllm_service import get_bot_userllm
from ..model.chat_message_model import ChatMessageDatabase, ChatMessageIn, ChatMessageOut

from ...core.models.user_claims_model import Jwt, UserClaims
from quart import Blueprint, current_app, websocket

from ..services.broker import Broker

from quart_jwt_extended import (
    decode_token,
    jwt_required,
    get_jwt_claims,
    get_jwt_identity
)

from app.llm_chat.services.llm import runllm_with_rag
chat_bp = Blueprint('chat', __name__)

broker = Broker()

@chat_bp.get('/messages/bot/<bot_id>')
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

@chat_bp.put('/datasource/<bot_id>/<datasource_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(Success, 200)
@validate_response(Failure, 401)
@validate_response(Failure, 400)
async def bot_change_datasource(bot_id: str, datasource_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    try:
        UserClaims.model_validate(user_claims)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user  unauthenticated"), 401
    bot_id_int: int
    datasource_id_int: int
    try:
        bot_id_int = int(bot_id)
        datasource_id_int = int(datasource_id)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Bad request"), 400
    datasource_name = await get_bot_datasource(user_id=current_user,datasource_id=datasource_id_int,bot_id=bot_id_int)
    if isinstance(datasource_name, str):
        pass
    else:
        return datasource_name

@chat_bp.delete('user/<bot_id>/<remove_user_id>')
@jwt_required
@validate_headers(Headers)
@validate_response(Success, 200)
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
    try:
        del broker.websocket_bots[bot_id_int][remove_user_id_int]
    except Exception as e:
        logging.critical(e.__str__())
    return Success(msg="Removed"), 200

async def _receive(bot_id: int, user_name: str, user_id: int, llm: str, datasource_id: Optional[int] = None) -> None:
    while True:
        msg: ChatMessageIn = await websocket.receive_as(ChatMessageIn)  # type: ignore
        
        in_id = str(uuid.uuid4())
        sent_id = str(uuid.uuid4())
        date_time_now = datetime.now()
        print(user_name)
        if user_id not in broker.websocket_bots[bot_id]:
            messageOut = ChatMessageOut(message_id=sent_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            message_text="User is removed from bot",
                                            notification=True,
                                            created=date_time_now,
                                            modified=date_time_now)
            await websocket.send_as(messageOut, ChatMessageOut) # type: ignore
            await websocket.send_as(Failure(error="User is removed from bot"), Failure) #type: ignore
            await websocket.close(401, 'User is removed from bot')
            return
        await broker.publish(ChatMessageOut(message_id=in_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            user_id_out=msg.user_id_in,
                                            message_text=msg.message_text,
                                            created=date_time_now,
                                            modified=date_time_now,
                                            message_user_name=user_name))
        await broker.publish(ChatMessageOut(message_id=sent_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            message_text='\U0001F914',
                                            created=date_time_now,
                                            modified=date_time_now))
        q_and_a = (msg.message_text, [])
        if not msg.notification:
            resp = runllm_with_rag(msg.message_text, bot_id)
            date_time_now = datetime.now()
            async for chunk in resp:
                messageOut = ChatMessageOut(message_id=sent_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            message_text=chunk,
                                            created=date_time_now,
                                            modified=date_time_now)
                await broker.publish(messageOut)
                q_and_a[1].append(chunk)
        bot_answer  = None
        if len(q_and_a[1]) > 0:
            bot_answer = ''.join(q_and_a[1])
        database_save_message = ChatMessageDatabase(user_message=q_and_a[0],
                                                    notification=msg.notification,
                                                    bot_answer=bot_answer,
                                                    user_id=user_id,
                                                    bot_id=bot_id,
                                                    datasource_id=datasource_id,
                                                    llm=llm)
        await save_message(msg=database_save_message)

@chat_bp.websocket('/ws/bot/<bot_id>')
async def wss(bot_id: str) -> Any:
    bot_id_int: int
    user_name: str
    user_id: int
    await websocket.accept(subprotocol='authorization')  
    try:
        bot_id_int = int(bot_id)
        jwt = websocket.requested_subprotocols[1]
        decoded_token = decode_token(jwt)
        jwt_token_obj = Jwt.model_validate(decoded_token)
        user_id = jwt_token_obj.identity
        user_name = jwt_token_obj.user_claims.full_name
    except Exception as e:
        await websocket.send_as(Failure(error="Not auhtorized"), Failure) #type: ignore
        await websocket.close(401, 'Not auhtorized')
        return
    if not user_id or not user_name:
        await websocket.send_as(Failure(error="Not auhtorized"), Failure) #type: ignore
        await websocket.close(401, 'Not auhtorized')
        return
    
    bot_user_llm = await get_bot_userllm(bot_id=bot_id_int, user_id=user_id)
    if isinstance(bot_user_llm, BotUserLlm):
        pass
    else:
        error, code = bot_user_llm
        await websocket.send_as(error, Failure) #type: ignore
        await websocket.close(code, error.error)
        return
    
    llm_assigned = get_lc_llm(bot_user_llm=bot_user_llm)
    if llm_assigned:
        try:
            llm_instance_for_bot_dict = current_app.config['LC_LLM_INSTANCE_COLLECTION_FOR_BOT']
            llm: BaseChatModel = llm_instance_for_bot_dict[bot_user_llm.bot_id]
            llm.invoke(input='Hello')
        except Exception as e:
            logging.critical(e.__str__())
            await websocket.send_as(Failure(error="Can not connect to LLM"), Failure) #type: ignore
            await websocket.close(400, 'Can not connect to LLM, Please check LLM configuration')
            return
    else:
        logging.critical('LLM is not assigned')
        await websocket.send_as(Failure(error="Can not connect to LLM"), Failure) #type: ignore
        await websocket.close(400, 'Can not connect to LLM, Please check LLM configuration')
    
    if bot_user_llm.datasource_id and bot_user_llm.datasource_name:
        await get_pgvector_instance(datasource_id=bot_user_llm.datasource_id,
                                            datasource_name=bot_user_llm.datasource_name, bot_id=bot_id_int)
    else:
        bot_pg_vector_collection = current_app.config['LC_PG_VECTOR_INSTANCE_COLLECTION_FOR_BOT']
        bot_pg_vector_collection[bot_id_int] = None
    try:
        task = asyncio.ensure_future(_receive(bot_id=bot_id_int, user_name=user_name, user_id=user_id, llm=f'{bot_user_llm.llmmodeltype_name}-{bot_user_llm.llm_name}', datasource_id=bot_user_llm.datasource_id))
        async for message in broker.subscribe(bot_id=bot_id_int, user_id=user_id):
            await websocket.send_as(message, ChatMessageOut)  # type: ignore
    finally:
        print('canceled')
        task.cancel() # type: ignore
        await task # type: ignore