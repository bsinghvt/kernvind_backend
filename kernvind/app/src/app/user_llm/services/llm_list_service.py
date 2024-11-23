import logging
from typing import List

from data_models.llm_model import Llm
from ...core.models.error_model import Failure

from ..models.user_llm_model import LlmListOut

async def get_available_model_list_service():
    try:
        llm_list = await Llm.all().prefetch_related('llmmodeltype')
        llm_out_list: List[LlmListOut] = []
        for llm in llm_list:
            llm_out_list.append(LlmListOut(llm_name=llm.llm_name,
                                        llmmodeltype_name=llm.llmmodeltype.llmmodeltype_name,
                                        created=llm.created,
                                        modified=llm.modified))
        return llm_out_list, 200
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong please try again"), 500