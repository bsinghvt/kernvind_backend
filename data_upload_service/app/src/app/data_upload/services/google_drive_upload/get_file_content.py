import io
from typing import Any
from googleapiclient.http import MediaIoBaseDownload
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from ...models.document_metadata_model import MetaData

from ..utils.unstructure_processing import UnstructureProcess

async def get_file_content(user_info: dict, file_id: str, mime_type: str, metadata: MetaData):
    try:
        request: Any
        creds = ServiceAccountCredentials.from_json_keyfile_dict(user_info)
        service = build("drive", "v3", credentials=creds)
        if mime_type == 'application/vnd.google-apps.document':
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            request = service.files().export_media(fileId=file_id,  mimeType=mime_type)
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            request = service.files().export_media(fileId=file_id,  mimeType=mime_type)
        else:
            request = service.files().get_media(fileId=file_id)   
        
        fh = io.BytesIO()
        done = False
        
        downloader = MediaIoBaseDownload(fh, request)
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)
        unstructured_process = UnstructureProcess(fh=fh, mime_type=mime_type, meta_data=metadata)
        text = await unstructured_process.partition()
        fh.close()
        return text
    except HttpError as error:
        logging.error(error.__str__())
        raise error
    except Exception as e:
        logging.error(e.__str__())
        raise e