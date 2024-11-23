import logging
from ..model.chat_message_model import ChatMessageDatabase
from data_models.chat_message_model import ChatMessage


async def save_message(msg: ChatMessageDatabase):
    is_bot_question = True
    try:
        if msg.notification:
            is_bot_question = False
        await ChatMessage.create(user_message=msg.user_message,
                                is_notification=msg.notification,
                                is_bot_question=is_bot_question,
                                bot_answer=msg.bot_answer,
                                bot_id=msg.bot_id,
                                llm=msg.llm,
                                datasource_id=msg.datasource_id,
                                user_id=msg.user_id)
    except Exception as e:
        logging.error(e.__str__())