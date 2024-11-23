import logging

from quart import current_app

from ....models.google_drive_auth_token_model import GoogleDriveAuthToken

from google_auth_oauthlib.flow import Flow
import json

GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/drive.readonly',
        'openid',
        'https://www.googleapis.com/auth/userinfo.profile']

async def get_google_drive_user_token(access_key: str):
    google_sec: str = current_app.config['GOOGLE_SEC']
    if not google_sec:
        raise Exception('Error with google drive auth')
    if not access_key:
        raise Exception('Access key is missing')
    try:
        flow = Flow.from_client_config(client_config=json.loads(google_sec), scopes=GOOGLE_DRIVE_SCOPES) # type: ignore
        flow.fetch_token(code=access_key)
        user_creds = flow.credentials.to_json()
        drive_auth_model = GoogleDriveAuthToken.model_validate_json(user_creds)
        return drive_auth_model.model_dump_json()
    except Exception as e:
        logging.critical(e.__str__())
        resp = Exception('Error with google drive auth')
        raise resp