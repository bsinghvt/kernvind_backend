import logging

from ...core.models.success_model import Success

from ...core.models.error_model import Failure
from data_models.bot_model import Bot


async def bot_delete(bot_id: int, user_id: int):
    try:
        new_bot = await Bot.filter(bot_id=bot_id, created_by_user_id=user_id).delete()
        print(new_bot)
        if new_bot:
            return  Success(msg='Bot is deleted')
        else:
            logging.error(f'Bot {bot_id,} is unauthorized delete')
            return Failure(error="Unauthorized bot."), 401
        
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong. Please try again"), 500 