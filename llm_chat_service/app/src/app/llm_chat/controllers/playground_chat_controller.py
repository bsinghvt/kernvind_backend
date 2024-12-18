import asyncio
import logging
from typing import Any, Optional
import uuid
from collections import deque

from ..services.playground.delete_playground_data import playground_data_delete
from ...core.models.playground_jwt_model import PlaygroundJwt
from ..model.playground_chat_message_model import PlaygroundChatMessage
from ..services.playground.get_playground_llm_service import get_playground_llm
from ..services.playground.playground_llm_rag import runllm_playground_with_rag

from ...core.models.error_model import Failure

from quart import Blueprint, current_app, websocket

from ..services.broker import Broker

from quart_jwt_extended import (
    decode_token,
)

playground_chat_bp = Blueprint('playground_chat', __name__)

broker = Broker()

async def _receive(bot_id: str, datasource_id: str) -> None:
    chat_history = deque(maxlen=4)
    while True:
        msg: Optional[PlaygroundChatMessage] = None
        try:
            msg = await websocket.receive_as(PlaygroundChatMessage)  # type: ignore
        except Exception as e:
            logging.error(e.__str__())
        if not msg:
            await websocket.send_as(Failure(error="Error while receiving message"), Failure) #type: ignore
            await websocket.close(500, 'Error while receiving message')
            raise Exception('Error while receiving message')
        
        in_id = str(uuid.uuid4())
        sent_id = str(uuid.uuid4())
        q_and_a = (msg.message_text, [])
        if not msg.first_message:
            await broker.publish(PlaygroundChatMessage(message_id=in_id, 
                                            bot_id=msg.bot_id,
                                            message_text=msg.message_text,
                                            message_user_name='Guest'))
            await broker.publish(PlaygroundChatMessage(message_id=sent_id, 
                                            message_user_name='AI Bot',
                                            bot_id=msg.bot_id,
                                            message_text='\U0001F914',
                                            ))
            llm = current_app.config['PLAYGROUND_LLM_CONFIG_DICT'].get(bot_id, None)
            resp = runllm_playground_with_rag(msg.message_text, datasource_name=datasource_id, chat_history=chat_history,llm=llm)
            async for chunk in resp:
                messageOut = PlaygroundChatMessage(message_id=sent_id, 
                                            message_user_name='AI Bot',
                                            bot_id=msg.bot_id,
                                            message_text=chunk,)
                await broker.publish(messageOut)
                q_and_a[1].append(chunk)

            await broker.publish(PlaygroundChatMessage(message_id=sent_id, 
                                            message_user_name='AI Bot',
                                            bot_id=msg.bot_id,
                                            message_text='||END||',
                                            ))
            bot_answer  = None
            if len(q_and_a[1]) > 0:
                bot_answer = ''.join(q_and_a[1])
            if bot_answer and "I don't have enough information to answer this question" not in bot_answer:
                chat_history.append((msg.message_text, bot_answer))
        else:
            current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id] = msg.llm_config
            is_connected = get_playground_llm(bot_id=msg.bot_id)
            if not is_connected:
                await websocket.send_as(Failure(error="Can not connect to LLM"), Failure) #type: ignore
                await websocket.close(400, 'Can not connect to LLM, Please check LLM configuration')
                raise Exception('LLM connection failed')
            else:
                await broker.publish(PlaygroundChatMessage(message_id=sent_id, 
                                            message_user_name='AI Bot',
                                            bot_id=msg.bot_id,
                                            message_text='Connected, you may start asking questions.',
                                            ))
                await broker.publish(PlaygroundChatMessage(message_id=sent_id, 
                                            message_user_name='AI Bot',
                                            bot_id=msg.bot_id,
                                            message_text='||END||',
                                            ))

@playground_chat_bp.websocket('/ws/playground/<bot_id>')
async def wss(bot_id: str) -> Any:
    datasource_name: Optional[str]
    await websocket.accept(subprotocol='authorization')  
    try:
        jwt = websocket.requested_subprotocols[1]
        decoded_token = decode_token(jwt)
        jwt_token_obj = PlaygroundJwt.model_validate(decoded_token)
        datasource_name = jwt_token_obj.identity
    except Exception as e:
        await websocket.send_as(Failure(error="Not auhtorized"), Failure) #type: ignore
        await websocket.close(401, 'Not auhtorized')
        logging.error(e.__str__())
        return
    if not datasource_name:
        await websocket.send_as(Failure(error="Not auhtorized"), Failure) #type: ignore
        await websocket.close(401, 'Not auhtorized')
        return
    
    try:
        task = asyncio.ensure_future(_receive(bot_id=bot_id, datasource_id=datasource_name))
        async for message in broker.subscribe(bot_id=bot_id, user_id=bot_id):
            await websocket.send_as(message, PlaygroundChatMessage)  # type: ignore
    except Exception as e:
        logging.error(e.__str__())
        try:
            await websocket.send_as(Failure(error="Chat server error"), Failure) #type: ignore
            await websocket.close(500, 'Chat server error')
        except Exception as e:
            logging.error(e.__str__())
    finally:
        await playground_data_delete(datasource_name=datasource_name)
        try:
            task.cancel() # type: ignore
            await task # type: ignore
        except Exception as e:
            logging.error(e.__str__())