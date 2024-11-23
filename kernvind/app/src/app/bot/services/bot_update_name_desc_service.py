import logging

from .get_bot_details_service import get_bot_details

from ..models.bot_update_name_desc_model import BotUpdateNameDescIn
from ...core.models.error_model import Failure
from data_models.bot_model import Bot
from tortoise.exceptions import IntegrityError


async def bot_update_name_desc(bot_in: BotUpdateNameDescIn, user_id: int):
    try:
        new_bot = await Bot.filter(bot_id=bot_in.bot_id, created_by_user_id=user_id).update(bot_name=bot_in.bot_name, bot_description=bot_in.bot_description)
        print(new_bot)
        print(bot_in)
        if new_bot:
            return await get_bot_details(bot_id=bot_in.bot_id, user_id=user_id)
        else:
            logging.error(f'Bot {bot_in.bot_id,} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'duplicate key' in err:
            return Failure(error="bot name already exists"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong. Please try again"), 500 