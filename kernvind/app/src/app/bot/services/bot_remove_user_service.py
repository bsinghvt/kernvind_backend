import logging
import httpx
from data_models.bot_model import BotUserXref, Bot, DataSource

from tortoise.exceptions import IntegrityError

from data_models.user_model import UserLlm

from .get_bot_details_service import get_bot_details

from ...core.models.error_model import Failure

from quart import current_app

async def bot_remove_user(user_id:int, bot_id: int, remove_user_id: int, token: str):
    if remove_user_id == user_id:
        return Failure(error="Bot owner can not be removed"), 401
    try:
        bot = await Bot.filter(bot_id=bot_id, created_by_user_id=user_id)
        if len(bot) == 0:
            return Failure(error="Only bot owner can remove user"), 401
        if bot[0].datasource_id: # type: ignore
            datasource = await DataSource.filter(datasource_id=bot[0].datasource_id, created_by_user_id=remove_user_id) # type: ignore
            if len(datasource) == 1:
                await Bot.filter(bot_id=bot_id, created_by_user_id=user_id).update(datasource_id=None)
        
        userLlm = await UserLlm.filter(user_llm_id=bot[0].user_llm_id, user_id=remove_user_id) # type: ignore
        if len(userLlm) > 0:
            return Failure(error="User is owner of bot LLM, so can't be removed"), 401
        
        botxref =  await BotUserXref.filter(user_id=remove_user_id, bot_id=bot_id).delete()
        chat_user_remove_url = current_app.config['BOT_CHAT_USER_REMOVE_URL']
        if botxref and chat_user_remove_url:
            try:
                async with httpx.AsyncClient() as client:
                    url = f'{chat_user_remove_url}/{bot_id}/{remove_user_id}'
                    headers = {
                    'Authorization' : token
                    }
                    response = await client.delete(url=url, headers=headers)
                
            except Exception as e:
                logging.critical(e.__str__())
            return await get_bot_details(bot_id=bot_id, user_id=user_id)
        else:
            logging.error(f'Bot {bot_id,} is unauthorized delete')
            return Failure(error="Unauthorized bot."), 401
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'duplicate key' in err:
            return Failure(error="user already exists in bot"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500