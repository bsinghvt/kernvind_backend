import asyncio
from datetime import datetime
import logging
from typing import Any, List, Optional
import uuid

from ..services.message_process import create_chat_message_out, process_llm_response

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
        try:
            # Receive a message
            incoming_message: ChatMessageIn = await websocket.receive_as(ChatMessageIn)  # type: ignore
            now = datetime.now()

            # Generate unique IDs for messages
            incoming_message_id = str(uuid.uuid4())
            outgoing_message_id = str(uuid.uuid4())

            # Check if the user is associated with the bot
            if user_id not in broker.websocket_bots.get(bot_id, []):
                await send_and_close_websocket(
                    bot_id, user_id, now, "User is removed from bot", 401
                )
                return

            # Publish the incoming message
            if incoming_message.bot_id > 0 and incoming_message.user_id_in > 0:
                await broker.publish(
                    create_chat_message_out(
                        incoming_message_id,
                        bot_id=incoming_message.bot_id,
                        user_id_in=user_id,
                        user_id_out=incoming_message.user_id_in,
                        message_text=incoming_message.message_text,
                        user_name=user_name,
                        created=now,
                        modified=now,
                    )
                )

            # Handle response if the message is not a notification
            if not incoming_message.notification:
                await broker.publish(
                    create_chat_message_out(
                        outgoing_message_id,
                        bot_id=incoming_message.bot_id,
                        user_id_in=user_id,
                        user_id_out=None,
                        message_text="\U0001F914",  # Thinking face emoji
                        created=now,
                        modified=now,
                    )
                )

                # Process the message with the LLM and handle response chunks
                await process_llm_response(
                    broker,
                    incoming_message,
                    bot_id,
                    user_id,
                    datasource_id,
                    llm,
                    outgoing_message_id,
                    now,
                )

        except Exception as e:
            logging.error(f"Error in _receive for bot_id={bot_id}, user_id={user_id}: {e}")
            await websocket.send_as(Failure(error=str(e)), Failure)  # type: ignore
            await websocket.close(500, "Internal Server Error")
            return


async def send_and_close_websocket(bot_id: int, user_id: int, now: datetime, message: str, code: int) -> None:
    """Send a message to the WebSocket and close the connection."""
    await websocket.send_as( # type: ignore
        create_chat_message_out(
            message_id=str(uuid.uuid4()),
            bot_id=bot_id,
            user_id_in=user_id,
            user_id_out=None,
            message_text=message,
            notification=True,
            created=now,
            modified=now,
        ),
        ChatMessageOut,
    )
    await websocket.send_as(Failure(error=message), Failure)  # type: ignore
    await websocket.close(code, message)
                
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
