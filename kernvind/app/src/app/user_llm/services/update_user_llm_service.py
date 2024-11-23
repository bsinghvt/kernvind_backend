import logging
from typing import Optional

from crypto_lib.aes_GCM import encrypt_AES_GCM

from .utils.verify_llm_connection import verify_llm

from .get_user_llm_details_service import get_user_llm_details_service

from ...core.models.error_model import Failure
from tortoise.exceptions import IntegrityError

from data_models.user_model import UserLlm

from ..models.user_llm_update_model import UserLlmUpdateIn


async def update_user_llm(user_llm_update_in: UserLlmUpdateIn):
    try:
        llm_config = user_llm_update_in.llm_config
        llm_config_json = llm_config.model_dump_json(exclude_none=True)
        user_llm: Optional[int] = None
        if llm_config_json == '{}':
            user_llm = await UserLlm.filter(user_id=user_llm_update_in.user_id, user_llm_id=user_llm_update_in.user_llm_id).update(llm_id=user_llm_update_in.llm_id,
                                        user_llm_name=user_llm_update_in.user_llm_name,
                                        user_llm_description=user_llm_update_in.user_llm_description,
                                        user_id=user_llm_update_in.user_id,)
        else:
            try:
                verify_llm(llm_config=user_llm_update_in.llm_config,
                        llmmodeltype_name=user_llm_update_in.llm_type,
                        llm_name=user_llm_update_in.llm_id)
            except Exception as e:
                return Failure(error="Not able to connect to LLM, please verify configuration"), 400
            kdf_salt, ciphertext, nonce, auth_tag = encrypt_AES_GCM(data = llm_config_json.encode())
            user_llm = await UserLlm.filter(user_id=user_llm_update_in.user_id, user_llm_id=user_llm_update_in.user_llm_id).update(llm_id=user_llm_update_in.llm_id,
                                        user_llm_name=user_llm_update_in.user_llm_name,
                                        user_llm_description=user_llm_update_in.user_llm_description,
                                        user_id=user_llm_update_in.user_id,
                                        llm_config_cipher=ciphertext,
                                        kdf_salt=kdf_salt,
                                        nonce=nonce,
                                        auth_tag=auth_tag)
        if user_llm:
            return await get_user_llm_details_service(user_llm_id=user_llm_update_in.user_llm_id, user_id=user_llm_update_in.user_id)
        else:
            logging.error(f'Bot {user_llm_update_in.user_llm_id,} is unauthorized')
            return Failure(error="Unauthorized user llm."), 401
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'duplicate key' in err:
            return Failure(error="userl llm name already exists"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong. Please try again"), 500 