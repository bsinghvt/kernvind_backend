import asyncio
from datetime import datetime
import logging
from typing import Any, List, Optional
import uuid

from ..services.get_bot_messages_service import get_bot_messages
from ..services.save_message_service import save_message
from langchain_core.language_models.chat_models import BaseChatModel

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

@chat_bp.get('/health')
async def health_check()->Any:
    return 'ok'

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

"""
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
"""

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
        if msg.bot_id > 0 and msg.user_id_in > 0:
            await broker.publish(ChatMessageOut(message_id=in_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            user_id_out=msg.user_id_in,
                                            message_text=msg.message_text,
                                            created=date_time_now,
                                            modified=date_time_now,
                                            message_user_name=user_name))
 
        q_and_a = (msg.message_text, [])
        if not msg.notification:
            await broker.publish(ChatMessageOut(message_id=sent_id, 
                                            bot_id=msg.bot_id,
                                            user_id_in=msg.user_id_in,
                                            message_text='\U0001F914',
                                            created=date_time_now,
                                            modified=date_time_now))
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
            if bot_answer and "I don't have enough information to answer this question" not in bot_answer:
                database_save_message = ChatMessageDatabase(user_message=q_and_a[0],
                                                    notification=msg.notification,
                                                    bot_answer=bot_answer,
                                                    user_id=user_id,
                                                    bot_id=bot_id,
                                                    datasource_id=datasource_id,
                                                    llm=llm)
                await save_message(msg=database_save_message)
                
def decode_jwt(token: str) -> dict:
    return decode_token(token)

def test_llm(input: str, bot_id: int) -> Any:
    llm_instance_collection = current_app.config['LC_LLM_INSTANCE_COLLECTION_FOR_BOT']
    llm: BaseChatModel = llm_instance_collection[bot_id]
    return llm.invoke(input=input)

@chat_bp.websocket('/ws/bot/<bot_id>')
async def websocket_handler(bot_id: str) -> None:
    headers = websocket.headers
    if "authorization" in websocket.requested_subprotocols:
        await websocket.accept(subprotocol="authorization")
    else:
        await websocket.accept()  # Accept without a subprotocol
    # Initialize variables
    try:
        bot_id_int = int(bot_id)
    except ValueError:
        await _close_websocket(400, "Invalid bot_id format")
        return

    try:
        # Validate JWT and extract user details
        if len(websocket.requested_subprotocols) > 1:
            jwt = websocket.requested_subprotocols[1]
        else:
            jwt = headers.get('Authorization', '').replace('Bearer ', '')
        decoded_token = decode_jwt(jwt)
        jwt_token_obj = Jwt.model_validate(decoded_token)
        user_id = jwt_token_obj.identity
        user_name = jwt_token_obj.user_claims.full_name
    except Exception as e:
        logging.warning(f"Authorization failed: {e}")
        await _close_websocket(401, "Not authorized")
        return

    if not user_id or not user_name:
        logging.warning("Missing user_id or user_name in JWT token")
        await _close_websocket(401, "Not authorized")
        return

    # Fetch bot-user LLM configuration
    bot_user_llm = await get_bot_userllm(bot_id=bot_id_int, user_id=user_id)
    if not isinstance(bot_user_llm, BotUserLlm):
        error, code = bot_user_llm
        logging.error(f"Failed to get bot-user LLM: {error}")
        await _close_websocket(code, error.error)
        return

    # Verify and connect to LLM
    llm_assigned = get_lc_llm(bot_user_llm=bot_user_llm)
    if llm_assigned:
        try:
            test_llm(input='Hello', bot_id=bot_user_llm.bot_id)  # Test LLM connectivity
        except Exception as e:
            logging.critical(f"LLM connection failed: {e}")
            await _close_websocket(400, "Cannot connect to LLM. Please check LLM configuration.")
            return
    else:
        logging.critical("No LLM assigned to the bot")
        await _close_websocket(400, "LLM not assigned. Please check LLM configuration.")
        return

    # Configure PGVector instance if necessary
    if bot_user_llm.datasource_id and bot_user_llm.datasource_name:
        get_pgvector_instance(
            datasource_id=bot_user_llm.datasource_id,
            datasource_name=bot_user_llm.datasource_name,
            bot_id=bot_id_int
        )
    else:
        pg_vector_collection = current_app.config['LC_PG_VECTOR_INSTANCE_COLLECTION_FOR_BOT']
        pg_vector_collection[bot_id_int] = None

    # Subscribe to broker and handle messages
    task = None
    try:
        task = asyncio.create_task(
            _receive(
                bot_id=bot_id_int,
                user_name=user_name,
                user_id=user_id,
                llm=f'{bot_user_llm.llmmodeltype_name}-{bot_user_llm.llm_name}',
                datasource_id=bot_user_llm.datasource_id,
            )
        )
        async for message in broker.subscribe(bot_id=bot_id_int, user_id=user_id):
            await websocket.send_as(message, ChatMessageOut)  # type: ignore
    except Exception as e:
        logging.error(f"Error during WebSocket communication: {e}")
    finally:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def _close_websocket(code: int, reason: str) -> None:
    """Helper function to close the WebSocket connection with an error."""
    await websocket.send_as(Failure(error=reason), Failure)  # type: ignore
    await websocket.close(code, reason)
