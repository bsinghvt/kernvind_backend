import logging
from crypto_lib.aes_GCM import decrypt_AES_GCM

from .google_drive_upload.extract_google_drive import extract_google_drive
from .youtube_transcript.extract_youtube_transcript import extract_youtube_transcript
from ..models.datafeed_apache_kafka_model import DataFeedApacheKafka
from ...config import Config
from sqlalchemy.ext.asyncio import AsyncEngine
from data_models.datasource_model import DataFeed

async def data_upload(config: Config, datafeed_msg: DataFeedApacheKafka, pg_async_engine: AsyncEngine):
    try:
        success = False
        if datafeed_msg.datafeedsource_id == 'Youtube video transcript':
            await extract_youtube_transcript(datafeedsource_id=datafeed_msg.datafeedsource_id,
                                    datafeed_source_unique_id=datafeed_msg.datafeed_source_unique_id,
                                    datafeed_source_title=datafeed_msg.datafeed_source_title,
                                    datafeed_id=datafeed_msg.datafeed_id,
                                    datasource_id=datafeed_msg.datasource_id,
                                    engine=pg_async_engine,
                                    config=config,
                                    datasource_name=datafeed_msg.datasource_name)
            success = True
        elif datafeed_msg.datafeedsource_id == 'Google drive':
            if datafeed_msg.kdf_salt and datafeed_msg.ciphertext and datafeed_msg.nonce and datafeed_msg.auth_tag:
                decrypt_raw: bytes =  decrypt_AES_GCM(kdf_salt= bytes.fromhex(datafeed_msg.kdf_salt),
                            ciphertext=bytes.fromhex(datafeed_msg.ciphertext),
                            nonce=bytes.fromhex(datafeed_msg.nonce),
                            auth_tag=bytes.fromhex(datafeed_msg.auth_tag))
                print(decrypt_raw.decode())
                await extract_google_drive(datafeedsource_id=datafeed_msg.datafeedsource_id,
                                    datafeed_source_unique_id=datafeed_msg.datafeed_source_unique_id,
                                    datafeed_id=datafeed_msg.datafeed_id,
                                    datasource_id=datafeed_msg.datasource_id,
                                    engine=pg_async_engine,
                                    config=config,
                                    datasource_name=datafeed_msg.datasource_name,
                                    user_token=decrypt_raw.decode())
                success = True
            else:
                logging.error('Creds are missing')
        if success == True:
            await DataFeed.filter(datafeed_id=datafeed_msg.datafeed_id).update(datafeedloadstatus_id='LOADED')
    except Exception as e:
        try:
            await DataFeed.filter(datafeed_id=datafeed_msg.datafeed_id).update(datafeedloadstatus_id='ERROR')
        except Exception as ie:
            logging.error(ie.__str__())
        logging.error(e.__str__())