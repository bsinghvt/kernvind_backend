import logging

from quart import current_app
from ...model.playground_chat_message_model import  LlmConfig
from ....core.constants.llm_constants import OLLAMA, OPENAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

def get_playground_llm(bot_id: str):
    llm_config: LlmConfig = current_app.config['PLAYGROUND_LLM_CONFIG_DICT'].get(bot_id, None)
    current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id] = None
    if not llm_config:
        return False
    if not isinstance(llm_config, LlmConfig):
        return False
    if llm_config.use_my_llm:
        llm_name: str = llm_config.llm_name # type: ignore
        try:
            if llm_config.llm_type == OLLAMA:
                auth = None
                headers = None
                if llm_config.user_name and llm_config.password:
                    auth=(llm_config.user_name, llm_config.password)
                if llm_config.api_key and llm_config.api_key_header:
                    headers = {
                            llm_config.api_key : llm_config.api_key_header
                            }
                client_kwargs = {}
                if auth:
                    client_kwargs['auth'] = auth
                if headers:
                    client_kwargs['headers'] = headers
                    
                current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id] = ChatOllama(
                    model = llm_name,
                    temperature=0,
                    base_url = llm_config.url,
                    client_kwargs = client_kwargs
                )
            elif llm_config.llm_type == OPENAI:
                current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id] = ChatOpenAI(
                    model = llm_name,
                    temperature=0,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                    api_key = llm_config.api_key # type: ignore
                    )
        except Exception as e:
            logging.critical(e.__str__())
            raise
    else:
        logging.info('connecting open ai')
        current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id] = ChatOpenAI(
                    model = current_app.config['PLAYGROUND_LLM_MODEL'],
                    temperature=0.5,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                    api_key =current_app.config['OPEN_AI_KEY'] # type: ignore
                    )
    if not current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id]:
        return False
    try:
        llm: BaseChatModel = current_app.config['PLAYGROUND_LLM_CONFIG_DICT'][bot_id]
        llm.invoke(input='Hello')
    except Exception as e:
        logging.critical(e.__str__())
        return False
    return True