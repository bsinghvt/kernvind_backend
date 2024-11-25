
import logging
from typing import  Optional, cast

from data_models.datasource_model import DataFeed
from ..model.bot_user_llm_model import BotUserLlm, LlmConfig
from data_models.bot_model import Bot, BotUserXref, DataSource
from data_models.user_model import  UserLlm
from tortoise.query_utils import Prefetch
from ...core.models.error_model import Failure
from crypto_lib.aes_GCM import decrypt_AES_GCM

async def get_bot_userllm(bot_id: int, user_id: int):
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id)
        if len(botxrefs) == 0 or len(botxrefs) > 1:
            logging.error(f'Bot {bot_id} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        
        user_llm_prefetch =  Prefetch('user_llm', queryset=UserLlm.all().only('user_llm_id','llm_id','llm_config_cipher','kdf_salt','nonce','auth_tag').prefetch_related('llm'))
        bot_user_llm = await Bot.filter(bot_id=bot_id).prefetch_related(
            'datasource', 
            user_llm_prefetch
        )
        if len(bot_user_llm) == 0 or len(bot_user_llm) > 1:
            logging.error(f'Bot {bot_id} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        
        user_llm =  cast(UserLlm, bot_user_llm[0].user_llm)
        datasource_id: Optional[int] = None
        datasource_name: Optional[str] = None

        if bot_user_llm[0].datasource:
            datasource = cast(DataSource, bot_user_llm[0].datasource)
            datafeed = await DataFeed.filter(datasource_id=datasource.datasource_id, datafeedloadstatus_id='LOADED').first()
            if datafeed:
                datasource_id = datasource.datasource_id
                datasource_name = datasource.datasource_name
            
        user_llm_id = user_llm.user_llm_id
        llm_name = user_llm.llm.llm_name
        llm_type_name = user_llm.llm.llmmodeltype_id
        llm_config_cipher = user_llm.llm_config_cipher
        kdf_salt = user_llm.kdf_salt
        nonce = user_llm.nonce
        auth_tag = user_llm.auth_tag
        llm_config_raw = decrypt_AES_GCM(kdf_salt=kdf_salt,ciphertext=llm_config_cipher,nonce=nonce,auth_tag=auth_tag)
        llm_config = LlmConfig.model_validate_json(llm_config_raw)
        return BotUserLlm(bot_id=bot_id,llm_name=llm_name,llmmodeltype_name=llm_type_name,llm_config=llm_config,
                        datasource_id=datasource_id,
                        datasource_name=datasource_name, user_llm_id=user_llm_id)
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500