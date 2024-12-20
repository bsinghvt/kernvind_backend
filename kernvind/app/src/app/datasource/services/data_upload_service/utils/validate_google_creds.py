import logging
from typing import Optional

import json

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

GOOGLE_DRIVE_SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

FILE_MIME_TYPE_QUERY = ("(mimeType='application/msword'"
        " or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
        " or mimeType='application/vnd.ms-excel'"
        " or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        " or mimeType='application/vnd.google-apps.document'"
        " or mimeType='application/vnd.google-apps.spreadsheet'"
        " or mimeType='text/plain'"
        " or mimeType='text/csv'" 
        " or mimeType='application/pdf'" 
        ")")

async def google_drive_user_creds_validation(access_key: str, folder_id: str):
    parent_folder_query = f"'{folder_id}' in parents"
    query = f'{parent_folder_query} and {FILE_MIME_TYPE_QUERY}'
    try:
        key = json.loads(access_key)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key, scopes=GOOGLE_DRIVE_SCOPES)
        service = build("drive", "v3", credentials=creds)
    except Exception as e:
        logging.error(e.__str__())
        raise Exception('The Google service credentials JSON file is invalid.')
    try:
        res = service.files().get(fileId=folder_id, fields='id, name').execute()
        folder_name: Optional[str] = res.get('name', None)
    except Exception as e:
        raise Exception('Please ensure the Google Drive folder link is correct and that the folder is shared with the Google service account.')
    try:
        response = (
                service.files()
                .list(
                    pageSize=3,
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, size, mimeType, webViewLink, modifiedTime)",
                    orderBy='modifiedTime'
                )
                .execute()
                )
        files = response.get("files", [])
        if len(files) == 0:
            raise Exception(f'"{folder_name}" folder does not contain any PDF, text, or spreadsheet files') 
    except Exception as e:
        logging.error(e.__str__())
        err = e.__str__()
        if 'does not contain any PDF' in err:
            raise
        raise Exception('An error occurred. Please try again later.')
    return folder_name