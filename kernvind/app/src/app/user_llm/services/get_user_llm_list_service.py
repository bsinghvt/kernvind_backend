import logging
from typing import List
from data_models.user_model import UserLlm

from ...core.models.error_model import Failure

from ..models.user_llm_model import LlmConfig, UserLlmOut

async def get_user_llm_list_service(user_id: int):
    try:
        userLlmList = await UserLlm.filter(user_id=user_id).prefetch_related('llm')
        user_llm_out_list: List[UserLlmOut] = []
        for user_llm in userLlmList:
            user_llm_out_list.append(UserLlmOut(user_llm_id=user_llm.user_llm_id,
                                                user_id=user_id,
                                                user_llm_name=user_llm.user_llm_name,
                                                user_llm_description=user_llm.user_llm_description,
                                                llm_id=user_llm.llm.llm_name,
                                                llm_type=user_llm.llm.llmmodeltype_id,
                                                llm_config=LlmConfig(),
                                                created=user_llm.created,
                                                modified=user_llm.modified))
        return user_llm_out_list, 200
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong please try again"), 500
