import logging

from quart import current_app
from ..model.bot_user_llm_model import BotUserLlm, LlmConfig
from ...core.constants.llm_constants import OLLAMA, OPENAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

def get_lc_llm(bot_user_llm: BotUserLlm):
    
    bot_id = bot_user_llm.bot_id
    user_llm_id = bot_user_llm.user_llm_id
    llm_instance_dict = current_app.config['LC_LLM_INSTANCE_COLLECTION']

    if user_llm_id not in llm_instance_dict or not llm_instance_dict[user_llm_id]:
        try:
            if bot_user_llm.llmmodeltype_name == OLLAMA:
                llm_instance_dict[user_llm_id] = ChatOllama(
                    model = bot_user_llm.llm_name,
                    temperature=0,
                    base_url = bot_user_llm.llm_config.url,
                )
            elif bot_user_llm.llmmodeltype_name == OPENAI:
                llm_instance_dict[user_llm_id] = ChatOpenAI(
                    model = bot_user_llm.llm_name,
                    temperature=0,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                    api_key = bot_user_llm.llm_config.api_key # type: ignore
                    )
        except Exception as e:
            logging.critical(e.__str__())
            raise
    llm_instance_for_bot_dict = current_app.config['LC_LLM_INSTANCE_COLLECTION_FOR_BOT']
    llm_instance_for_bot_dict[bot_id] = llm_instance_dict[user_llm_id]
    return True