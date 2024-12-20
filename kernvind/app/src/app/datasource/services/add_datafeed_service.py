import logging
from typing import Optional

from .data_upload_service.utils.validate_google_creds import google_drive_user_creds_validation

from .data_upload_service.utils.validate_youtube_video import validate_youtube_video

from data_models.bot_model import DataSource
from data_models.datasource_model import DataFeed

from crypto_lib.aes_GCM import encrypt_AES_GCM

from .get_datasource_details_service import datasource_details

from ..models.datasource_datafeed_add_model import DataSourceAddFeed

from ...core.models.error_model import Failure
from tortoise.exceptions import IntegrityError
from tortoise.transactions import  in_transaction


async def add_datasource_feed(user_id: int, datasourceAddFeed: DataSourceAddFeed):
    if datasourceAddFeed.datafeedsource_id == 'Google drive' and datasourceAddFeed.access_key == None:
        return Failure(error="Access Key is missing"), 400
    access_key: str = datasourceAddFeed.access_key # type: ignore
    title: Optional[str] = None
    if datasourceAddFeed.datafeedsource_id == 'Youtube video transcript' and datasourceAddFeed.datafeed_source_title == 'FROM WEB':
        
        try:
            title = await validate_youtube_video(video_id=datasourceAddFeed.datafeed_source_unique_id)
            if not title:
                return Failure(error="Please make sure youtube link is valid and english captions are available and video is no longer than 6 hours"), 400
        except Exception as e:
            return Failure(error="Please make sure youtube link is valid and english captions are available and video is no longer than 6 hours"), 400
        datasourceAddFeed.datafeed_source_title  = title
    try:
        async with in_transaction() as connection:
            folder_name: str | None = None
            kdf_salt: bytes| None = None
            ciphertext: bytes| None = None
            nonce: bytes| None = None
            auth_tag: bytes| None = None
            if datasourceAddFeed.datafeedsource_id == 'Google drive':
                try:
                    folder_name = await google_drive_user_creds_validation(access_key=access_key, folder_id=datasourceAddFeed.datafeed_source_unique_id)
                except Exception as e:
                    logging.error(e.__str__())
                    err = e.__str__()
                    return Failure(error=err), 400
                
                if not isinstance(folder_name, str):
                    return Failure(error="An error occurred. Please try again later."), 500
                datasourceAddFeed.datafeed_source_title = folder_name
                kdf_salt, ciphertext, nonce, auth_tag = encrypt_AES_GCM(data = access_key.encode())
            datasource =  await DataSource.filter(created_by_user_id=user_id, datasource_id=datasourceAddFeed.datasource_id)
            if len(datasource) == 0:
                return Failure(error="User is Unauthorized to add datasource feed"), 401
            datasource_name = datasource[0].datasource_name
            
            new_feed = await DataFeed.create(datafeed_name = datasourceAddFeed.datafeed_name, 
                                    datafeed_source_unique_id = datasourceAddFeed.datafeed_source_unique_id, 
                                    datafeed_source_title = datasourceAddFeed.datafeed_source_title, 
                                    datafeed_description = datasourceAddFeed.datafeed_description, 
                                    datafeedsource_id = datasourceAddFeed.datafeedsource_id, 
                                    created_by_user_id = user_id, 
                                    datasource_id=datasource[0].datasource_id,
                                    kdf_salt=kdf_salt,
                                    nonce=nonce,
                                    datafeedsource_config_cipher=ciphertext,
                                    auth_tag=auth_tag
                                    )

            """
            await data_upload(datasource_name=datasource_name,
                            datafeedsource_id=datasourceAddFeed.datafeedsource_id,
                            datafeed_source_unique_id=datasourceAddFeed.datafeed_source_unique_id,
                            datasource_id=datasourceAddFeed.datasource_id,
                            datafeed_id=new_feed.datafeed_id)
            """
            
            logging.info(f'{datasource_name} created successfully by user {user_id}')
            
            return await datasource_details(user_id=user_id, datasource_id=datasourceAddFeed.datasource_id)
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'datafeed_datafeed_name_key' in err:
            return Failure(error="datafeed name already exists"), 409
        if 'datafeed_datasource_id_datafeed' in err:
            return Failure(error=f"datafeed source {datasourceAddFeed.datafeed_source_unique_id} already exists"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        err = e.__str__()
        if 'youtube link:' in err:
            return Failure(error=err), 400
        return Failure(error="Something went wrong. Please try again"), 500
