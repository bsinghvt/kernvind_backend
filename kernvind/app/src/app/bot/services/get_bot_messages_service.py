import logging
from typing import List

from ...core.models.error_model import Failure
from data_models.user_model import User

from data_models.bot_model import BotUserXref
from ..models.chat_message_model import ChatMessageOut
from data_models.chat_message_model import ChatMessage
from tortoise.query_utils import Prefetch

async def get_bot_messages(bot_id: int, user_id: int):
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id)
        if len(botxrefs) == 0 or len(botxrefs) > 1:
            logging.error(f'Bot {bot_id} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        msgs_out: List[ChatMessageOut] = []
        user_prefetch = Prefetch('user', queryset=User.all().only('full_name', 'user_id'))
        msgs = await ChatMessage.filter(bot_id=bot_id).order_by('-modified').limit(250).prefetch_related(user_prefetch)
        msgs.reverse()
        for msg in msgs:
            bot_id = msg.bot_id # type: ignore
            user_id = msg.user_id # type: ignore
            user_name = msg.user.full_name
            msgs_out.append(ChatMessageOut(message_id=f'q_{msg.chat_message_id}', 
                                            bot_id=bot_id,
                                            user_id_in=user_id,
                                            user_id_out=user_id,
                                            notification=msg.is_notification,
                                            message_text=msg.user_message,
                                            created=msg.created,
                                            modified=msg.modified,
                                            message_user_name=user_name))
            if msg.bot_answer:
                msgs_out.append(ChatMessageOut(message_id=f'a_{msg.chat_message_id}',
                                            bot_id=bot_id,
                                            user_id_in=user_id,
                                            message_text=msg.bot_answer,
                                            created=msg.created,
                                            modified=msg.modified))
        return msgs_out, 200
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500