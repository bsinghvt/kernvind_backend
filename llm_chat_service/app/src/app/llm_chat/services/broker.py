import asyncio
from typing import AsyncGenerator
from collections import defaultdict
from ..model.chat_message_model import ChatMessageOut

class Broker:
    def __init__(self) -> None:
        self.websocket_bots = defaultdict(lambda: defaultdict(asyncio.Queue))
        #self.question_request = defaultdict(int)

    async def publish(self, messageOut: ChatMessageOut) -> None:
        connections = self.websocket_bots[messageOut.bot_id].items()
        for user, connection in connections:
            await connection.put(messageOut)

    async def subscribe(self, bot_id: int, user_id: int) -> AsyncGenerator[str, None]:
        connection = asyncio.Queue()
        self.websocket_bots[bot_id][user_id] = connection
        try:
            while True:
                msg =  await connection.get()
                yield msg
        finally:
            print(f'connection  removed: {user_id}')
            try:
                del self.websocket_bots[bot_id][user_id]
            except:
                pass