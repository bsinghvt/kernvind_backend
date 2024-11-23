import logging
from typing import List

from ...core.models.success_model import Success
from data_models.bot_model import Bot

from ...core.models.error_model import Failure

from data_models.user_model import UserLlm
from tortoise.query_utils import Prefetch

async def delete_user_llm(user_llm_id: int, user_id: int):
    try:
        bots_prefetch =  Prefetch('bots_user_llm', queryset=Bot.all().only('bot_id','user_llm_id'))
        user_llm = await UserLlm.filter(user_id=user_id, user_llm_id=user_llm_id).prefetch_related(bots_prefetch).first()
        if not user_llm:
            return Failure(error="User is Unauthorized to delete llm"), 401
        bots: List[Bot]  = await user_llm.bots_user_llm.all().only('bot_id', 'user_llm_id')
        if len(bots) > 0:
            return Failure(error="LLM can't be deleted as it is linked to bot"), 400
        await UserLlm.filter(user_id=user_id, user_llm_id=user_llm_id).delete()
        return  Success(msg='LLM is deleted')
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong. Please try again"), 500 