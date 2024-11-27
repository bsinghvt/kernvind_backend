import logging
from typing import Optional

from crypto_lib.aes_GCM import encrypt_AES_GCM

from .data_upload_service.utils.validate_youtube_video import validate_youtube_video

from .data_upload_service.datasource_feeds.google_drive_user_token_service import get_google_drive_user_token
from data_models.bot_model import DataSource
from data_models.datasource_model import DataFeed

from ..models.new_datasource_models import DataSourceIn, DataSourceOut
from ...core.models.error_model import Failure
from tortoise.exceptions import IntegrityError
from tortoise.transactions import  in_transaction

async def create_datasource(datasource_in: DataSourceIn):
    
    if datasource_in.datasource_feed.datafeedsource_id == 'Google drive' and datasource_in.datasource_feed.access_key == None:
        return Failure(error="Access Key is missing"), 400
    access_key: str = datasource_in.datasource_feed.access_key # type: ignore
    title: Optional[str] = None
    if datasource_in.datasource_feed.datafeedsource_id == 'Youtube video transcript' and datasource_in.datasource_feed.datafeed_source_title == 'FROM WEB':
        title = await validate_youtube_video(video_id=datasource_in.datasource_feed.datafeed_source_unique_id)
        if not title:
            return Failure(error="Please make sure youtube link ia valid and english captions are available"), 400
        
        datasource_in.datasource_feed.datafeed_source_title  = title   
    try:
        async with in_transaction() as connection:
            user_token: str | None = None
            kdf_salt: bytes| None = None
            ciphertext: bytes| None = None
            nonce: bytes| None = None
            auth_tag: bytes| None = None
            is_creds = False
            if datasource_in.datasource_feed.datafeedsource_id == 'Google drive':
                is_creds = True
                user_token = await get_google_drive_user_token(access_key=access_key)
                kdf_salt, ciphertext, nonce, auth_tag = encrypt_AES_GCM(data = user_token.encode())
                
            new_datasource = await DataSource.create(datasource_name=datasource_in.datasource_name, 
                                        datasource_description=datasource_in.datasource_description,
                                        created_by_user_id=datasource_in.created_by_user_id,
                                        )
            
            new_feed = await DataFeed.create(datafeed_name = datasource_in.datasource_feed.datafeed_name, 
                                    datafeed_source_unique_id = datasource_in.datasource_feed.datafeed_source_unique_id, 
                                    datafeed_source_title = datasource_in.datasource_feed.datafeed_source_title, 
                                    datafeed_description = datasource_in.datasource_feed.datafeed_description, 
                                    datafeedsource_id = datasource_in.datasource_feed.datafeedsource_id, 
                                    created_by_user_id = datasource_in.datasource_feed.created_by_user_id, 
                                    datasource_id=new_datasource.datasource_id,
                                    kdf_salt=kdf_salt,
                                    nonce=nonce,
                                    datafeedsource_config_cipher=ciphertext,
                                    auth_tag=auth_tag
                                    )
            
            logging.info(f'{datasource_in.datasource_name} created successfully by user {datasource_in.created_by_user_id}, {datasource_in.created_by_name}')
            
            datasource_out_dict = datasource_in.model_dump()
            datasource_out_dict['created'] = new_datasource.created
            datasource_out_dict['modified'] = new_datasource.modified
            datasource_out_dict['datasource_id'] = new_datasource.datasource_id
            datasource_out_dict['datasource_feed']['datafeed_id'] = new_feed.datafeed_id
            datasource_out_dict['datasource_feed']['created'] = new_feed.created
            datasource_out_dict['datasource_feed']['modified'] = new_feed.modified
            
            return DataSourceOut.model_validate(datasource_out_dict), 201
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'datasource_datasource_name_key' in err:
            return Failure(error="datasource name already exists"), 409
        if 'datafeed_datafeed_name_key' in err:
            return Failure(error="datafeed name already exists"), 409
        if 'datafeed_datafeed_source_unique_id_datafeedsource_id' in err:
            return Failure(error=f"datafeed source {datasource_in.datasource_feed.datafeed_source_unique_id} already exists"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        err = e.__str__()
        if 'youtube link:' in err:
            return Failure(error=err)
        return Failure(error="Something went wrong. Please try again"), 500
