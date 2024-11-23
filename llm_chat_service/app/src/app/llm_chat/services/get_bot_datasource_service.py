
import logging
from data_models.bot_model import  BotUserXref, DataSource
from ...core.models.error_model import Failure

async def get_bot_datasource(bot_id: int, user_id: int, datasource_id: int):
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id, can_change_datasource=True)
        if len(botxrefs) == 0 or len(botxrefs) > 1:
            logging.error(f'Bot {bot_id} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        
        user_datasource = await DataSource.filter(datasource_id=datasource_id,created_by_user_id = user_id)
        if len(user_datasource) == 0 or len(user_datasource) > 1:
            logging.error(f'Datasource {datasource_id} is unauthorized')
            return Failure(error="Unauthorized datasource."), 401
        return user_datasource[0].datasource_name
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500