import logging
from typing import List
from data_models.user_model import UserLlm

from data_models.bot_model import Bot

from ..models.user_llm_details_model import UserLlmBotOut, UserLlmDetails

from ...core.models.error_model import Failure

from ..models.user_llm_model import LlmConfig, UserLlmOut
from tortoise.query_utils import Prefetch

async def get_user_llm_details_service(user_id: int, user_llm_id: int):
    try:
        bots_prefetch =  Prefetch('bots_user_llm', queryset=Bot.all().only('bot_id','bot_name','bot_description','user_llm_id'))
        user_llm = await UserLlm.filter(user_id=user_id, user_llm_id=user_llm_id).first().prefetch_related('llm', bots_prefetch)
        if not user_llm:
            return Failure(error="User is Unauthorized to get llm details"), 401
        bots: List[Bot] = await user_llm.bots_user_llm.all().only('bot_id', 'bot_name', 'bot_description')
        bot_list: List[UserLlmBotOut] = []
        for bot in bots:
            bot_list.append(UserLlmBotOut(bot_id=bot.bot_id,
                                        bot_name=bot.bot_name,
                                        bot_description=bot.bot_description))
            
        user_llm_out = UserLlmOut(user_llm_id=user_llm.user_llm_id,
                                                user_id=user_id,
                                                user_llm_name=user_llm.user_llm_name,
                                                user_llm_description=user_llm.user_llm_description,
                                                llm_id=user_llm.llm.llm_name,
                                                llm_type=user_llm.llm.llmmodeltype_id,
                                                llm_config=LlmConfig(),
                                                created=user_llm.created,
                                                modified=user_llm.modified)
        return UserLlmDetails(user_llm=user_llm_out, user_llm_bots=bot_list), 200
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong please try again"), 500
