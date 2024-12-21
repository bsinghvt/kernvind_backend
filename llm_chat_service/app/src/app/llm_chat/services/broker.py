import asyncio
import logging
from typing import AsyncGenerator, Union, Dict
from collections import defaultdict

from ..model.playground_chat_message_model import PlaygroundChatMessage
from ..model.chat_message_model import ChatMessageOut

DEFAULT_QUEUE_SIZE = 100

class Broker:
    def __init__(self) -> None:
        self.websocket_bots: Dict[
            Union[int, str], 
            Dict[Union[int, str], asyncio.Queue[Union[ChatMessageOut, PlaygroundChatMessage]]]
        ] = defaultdict(lambda: defaultdict(lambda: asyncio.Queue(maxsize=DEFAULT_QUEUE_SIZE)))

    async def publish(self, messageOut: Union[ChatMessageOut, PlaygroundChatMessage]) -> None:
        """Publish a message to all users connected to a bot."""
        try:
            connections = self.websocket_bots[messageOut.bot_id].items()
            for user, connection in connections:
                try:
                    await connection.put(messageOut)
                except asyncio.QueueFull as qf:
                    logging.warning(f"Queue full for user {user} in bot {messageOut.bot_id}: {qf}")
        except Exception as e:
            logging.error(f"Error publishing message to bot {messageOut.bot_id}: {e}")

    async def subscribe(self, bot_id: Union[int, str], user_id: Union[int, str]) -> AsyncGenerator[Union[ChatMessageOut, PlaygroundChatMessage], None]:
        """Subscribe a user to a bot and yield messages."""
        connection = asyncio.Queue()
        self.websocket_bots[bot_id][user_id] = connection
        try:
            while True:
                msg = await connection.get()
                yield msg
        except asyncio.CancelledError:
            logging.info(f"Subscription cancelled for user {user_id} in bot {bot_id}")
            raise
        except Exception as e:
            logging.error(f"Error in subscription for user {user_id} in bot {bot_id}: {e}")
        finally:
            logging.info(f"Connection removed: {user_id} from bot {bot_id}")
            try:
                del self.websocket_bots[bot_id][user_id]
                if not self.websocket_bots[bot_id]:
                    del self.websocket_bots[bot_id]
            except KeyError:
                logging.warning(f"User {user_id} not found in bot {bot_id}")
