import gc
import json
import logging
from data_models.datasource_model import DataFeed
from sqlalchemy.ext.asyncio import AsyncEngine

from app.data_upload.models.google_drive_file_metadata_model import GoogleDriveFileMetaData
from .get_file_content import get_file_content

from .google_drive_files_loop import google_drive_files_loop

from ....config import Config
from ..utils.pg_vector_upload import upload_vector_doc_pg
from ...models.document_metadata_model import MetaData

SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly",
    ]
ACCOUNT = ''


async def extract_google_drive(datafeed_source_unique_id: str,
                                    datafeedsource_id: str,
                                    datasource_name: str,
                                    datafeed_id: int,
                                    datasource_id: int,
                                    engine: AsyncEngine, 
                                    config: Config,
                                    user_token: str):
    try:
        user_info_dict = json.loads(user_token)
        async for google_drive_file in google_drive_files_loop(user_info=user_info_dict, 
                                    folder_id=datafeed_source_unique_id):
            if isinstance(google_drive_file, GoogleDriveFileMetaData):
                logging.info(f'Loading {google_drive_file.name } :  {google_drive_file.mime_type}')
                metadata=MetaData(source_id=google_drive_file.web_view_link,
                                source_title=google_drive_file.name,
                                datafeedsource_id=datafeedsource_id, 
                                datasource_id=datasource_id,
                                datafeed_id=datafeed_id)
                file_data = await get_file_content(user_info=user_info_dict,
                                    file_id=google_drive_file.file_id,
                                    mime_type=google_drive_file.mime_type, metadata=metadata)
                await upload_vector_doc_pg(engine=engine,
                                datasource_name=datasource_name,
                                config=config,
                                docs=file_data)
                logging.info(f'Loaded {google_drive_file.name } :  {google_drive_file.mime_type}')
                await DataFeed.filter(datafeed_id=datafeed_id).update(lastload_datetime=google_drive_file.modified_time)
                del file_data, metadata
                gc.collect()
                
    except Exception as e:
        resp = Exception(f'Error while connecting to google drive: {datafeed_source_unique_id}. {e.__str__()}')
        raise resp