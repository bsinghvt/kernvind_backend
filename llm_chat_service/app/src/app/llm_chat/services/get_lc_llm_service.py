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
    llm_user_llm_name_dict = current_app.config['LC_USER_LLM_NAME_INSTANCE_COLLECTION']
    create_new = False
    if user_llm_id in llm_user_llm_name_dict and bot_user_llm.llm_name != llm_user_llm_name_dict[user_llm_id]:
        create_new = True
    llm_user_llm_name_dict[user_llm_id] = bot_user_llm.llm_name

    if user_llm_id not in llm_instance_dict or not llm_instance_dict[user_llm_id] or create_new:
        try:
            if bot_user_llm.llmmodeltype_name == OLLAMA:
                auth = None
                headers = None
                if bot_user_llm.llm_config:
                    if bot_user_llm.llm_config.user_name and bot_user_llm.llm_config.password:
                        auth=(bot_user_llm.llm_config.user_name, bot_user_llm.llm_config.password)
                    if bot_user_llm.llm_config.api_key and bot_user_llm.llm_config.api_key_header:
                        headers = {
                            bot_user_llm.llm_config.api_key : bot_user_llm.llm_config.api_key_header
                            }
                client_kwargs = {}
                if auth:
                    client_kwargs['auth'] = auth
                if headers:
                    client_kwargs['headers'] = headers
                llm_instance_dict[user_llm_id] = ChatOllama(
                    model = bot_user_llm.llm_name,
                    temperature=0,
                    base_url = bot_user_llm.llm_config.url,
                    client_kwargs = client_kwargs
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