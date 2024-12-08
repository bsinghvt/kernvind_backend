import logging
from typing import Optional
from ...core.llm_constants import OLLAMA, OPENAI
from ...models.user_llm_model import LlmConfig
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import httpx

def verify_llm(llm_config: LlmConfig, llmmodeltype_name: str, llm_name: str):
    try:
        llm = None
        if llmmodeltype_name == OLLAMA:
            auth = None
            headers = None
            if llm_config:
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
            llm = ChatOllama(
                    model = llm_name,
                    base_url = llm_config.url,
                    client_kwargs = client_kwargs
                )
        elif llmmodeltype_name == OPENAI:
            llm = ChatOpenAI(
                    model = llm_name,
                    max_retries=2,
                    api_key = llm_config.api_key # type: ignore
                    )
        else:
            raise Exception(f'Wrong mode type: "{llmmodeltype_name}" or model name: "{llm_name}"')
        if not llm:
            raise Exception('Llm connection error')
        else:
            llm.invoke(input='Hello')
    except Exception as e:
        logging.critical(e.__str__())
        raise