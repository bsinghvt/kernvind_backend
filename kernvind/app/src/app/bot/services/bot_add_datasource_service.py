import logging

from data_models.bot_model import Bot, BotUserXref
from data_models.bot_model import DataSource

from .get_bot_details_service import get_bot_details

from ...core.models.error_model import Failure


async def bot_add_datasource(user_id:int, bot_id: int, datasource_id: int):
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id, can_change_datasource=True)
        if len(botxrefs) == 0:
            return Failure(error="User is Unauthorized to add datasource to bot"), 401
        if len(botxrefs) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        datasource =  await DataSource.filter(created_by_user_id=user_id, datasource_id=datasource_id)
        
        if len(datasource) == 0:
            return Failure(error="User is Unauthorized for datasource"), 401
        if len(datasource) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        await Bot.filter(bot_id=bot_id).update(datasource_id=datasource_id)
        return await get_bot_details(bot_id=bot_id, user_id=user_id)
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500