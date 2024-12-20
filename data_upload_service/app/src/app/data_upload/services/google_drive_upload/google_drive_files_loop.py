import gc
import logging
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...models.google_drive_file_metadata_model import GoogleDriveFileMetaData

FILE_MIME_TYPE_QUERY = ("(mimeType='application/msword'"
        " or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
        " or mimeType='application/vnd.ms-excel'"
        " or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        " or mimeType='application/vnd.google-apps.document'"
        " or mimeType='application/vnd.google-apps.spreadsheet'"
        " or mimeType='text/plain'"
        " or mimeType='text/csv'" 
        " or mimeType='application/pdf'" 
        " or mimeType='application/vnd.google-apps.folder'" 
        ")")
MAX_SUB_FOLDERS = 50
async def google_drive_files_loop(user_info: dict, folder_id: str):
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(user_info)
        service = build("drive", "v3", credentials=creds)
        page_token = None
        parent_folder_query = f"'{folder_id}' in parents"
        query = f'{parent_folder_query} and {FILE_MIME_TYPE_QUERY}'
        sub_folders = 0
        while True:
            response = (
                service.files()
                .list(
                    pageSize=500,
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, size, mimeType, webViewLink, modifiedTime)",
                    pageToken=page_token,
                    orderBy='modifiedTime'
                )
                .execute()
                )
            for file in response.get("files", []):
                if file.get("mimeType") == "application/vnd.google-apps.folder" and sub_folders <= MAX_SUB_FOLDERS:
                    sub_folders = sub_folders + 1
                    async for file in google_drive_files_loop(user_info=user_info, folder_id=file.get("id")):
                        yield file
                else:
                    yield GoogleDriveFileMetaData(file_id=file.get("id"),
                                        name=file.get("name"),
                                        mime_type=file.get("mimeType"),
                                        size=file.get("size"),
                                        web_view_link=file.get("webViewLink"),
                                        modified_time=file.get("modifiedTime")
                                        )
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
            del response
            gc.collect()
    except HttpError as error:
        logging.error(error.__str__())
        raise error
    except Exception as e:
        logging.error(e.__str__())
        raise e