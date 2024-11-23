import logging

from data_models.bot_model import Bot, BotUserXref

from data_models.user_model import UserLlm

from .get_bot_details_service import get_bot_details

from ...core.models.error_model import Failure


async def bot_change_llm(user_id:int, bot_id: int, user_llm_id: int):
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id, can_change_llm=True)
        if len(botxrefs) == 0:
            return Failure(error="User is Unauthorized to change LLM for bot"), 401
        if len(botxrefs) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        user_llm =  await UserLlm.filter(user_id=user_id, user_llm_id=user_llm_id)
        
        if len(user_llm) == 0:
            return Failure(error="User is Unauthorized for LLM"), 401
        if len(user_llm) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        await Bot.filter(bot_id=bot_id).update(user_llm_id=user_llm_id)
        return await get_bot_details(bot_id=bot_id, user_id=user_id)
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500