import logging
from typing import Optional
from ...core.llm_constants import OLLAMA, OPENAI
from ...models.user_llm_model import LlmConfig
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

def verify_llm(llm_config: LlmConfig, llmmodeltype_name: str, llm_name: str):
    try:
        llm = None
        print(llmmodeltype_name)
        print(llm_name)
        if llmmodeltype_name == OLLAMA:
            llm = ChatOllama(
                    model = llm_name,
                    base_url = llm_config.url,
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