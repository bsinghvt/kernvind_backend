import asyncio
import logging
from typing import AsyncGenerator
from collections import defaultdict

from ..model.playground_chat_message_model import PlaygroundChatMessage
from ..model.chat_message_model import ChatMessageOut

class Broker:
    def __init__(self) -> None:
        self.websocket_bots = defaultdict(lambda: defaultdict(asyncio.Queue))
        #self.question_request = defaultdict(int)

    async def publish(self, messageOut: ChatMessageOut | PlaygroundChatMessage) -> None:
        try:
            connections = self.websocket_bots[messageOut.bot_id].items()
            for user, connection in connections:
                await connection.put(messageOut)
        except Exception as e:
            logging.error(e.__str__())

    async def subscribe(self, bot_id: int | str, user_id: int | str) -> AsyncGenerator[str, None]:
        connection = asyncio.Queue()
        self.websocket_bots[bot_id][user_id] = connection
        try:
            while True:
                msg =  await connection.get()
                yield msg
        except Exception as e:
            logging.error(e.__str__())
        finally:
            print(f'connection  removed: {user_id}')
            try:
                del self.websocket_bots[bot_id][user_id]
            except:
                pass