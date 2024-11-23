import logging

from crypto_lib.aes_GCM import encrypt_AES_GCM

from .utils.verify_llm_connection import verify_llm
from ..models.user_llm_model import LlmConfig, UserLlmIn, UserLlmOut
from ...core.models.error_model import Failure
from data_models.user_model import UserLlm



async def create_user_llm_service(user_llm_in: UserLlmIn):
    try:
        llm_config = user_llm_in.llm_config
        llm_config_json = llm_config.model_dump_json(exclude_none=True)
        logging.info(llm_config)
        logging.info(llm_config_json)
        if llm_config_json == '{}':
            return Failure(error='LLM config is required')
        else:
            try:
                verify_llm(llm_config=user_llm_in.llm_config,
                        llmmodeltype_name=user_llm_in.llm_type,
                        llm_name=user_llm_in.llm_id)
            except Exception as e:
                return Failure(error="Not able to connect to LLM, please verify configuration"), 400
            kdf_salt, ciphertext, nonce, auth_tag = encrypt_AES_GCM(data = llm_config_json.encode())

        user_llm = await UserLlm.create(llm_id=user_llm_in.llm_id,
                                        user_llm_name=user_llm_in.user_llm_name,
                                        user_llm_description=user_llm_in.user_llm_description,
                                        user_id=user_llm_in.user_id,
                                        llm_config_cipher=ciphertext,
                                        kdf_salt=kdf_salt,
                                        nonce=nonce,
                                        auth_tag=auth_tag
                                    )
        return UserLlmOut(llm_id=user_llm_in.llm_id,
                            user_llm_name=user_llm_in.user_llm_name,
                            user_llm_description=user_llm_in.user_llm_description,
                            user_llm_id=user_llm.user_llm_id,
                            llm_type=user_llm_in.llm_type,
                            llm_config=LlmConfig(),
                            user_id=user_llm_in.user_id,
                            created=user_llm.created,
                            modified=user_llm.modified
                        ), 201
    except Exception as e:
        logging.critical(e)
        return Failure(error='Something went wrong, please try again'), 500

