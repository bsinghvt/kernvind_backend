import os
import json

def creds_load(app):
    app_creds_file = os.getenv('APP_CREDS_JSON_FILE')
    app_creds = os.getenv('APP_CREDS_JSON')
    json_str: str
    if app_creds_file:
        with open(app_creds_file, 'r') as reader:
            json_str = reader.read()
    elif app_creds:
        json_str = app_creds
    else:
        raise Exception('Error loading creds file')
    try:
        dict_obj = json.loads(json_str)
        app.config['JWT_PRIVATE_KEY'] = dict_obj['jwt_private_key']
        app.config['JWT_PUBLIC_KEY'] = dict_obj['jwt_public_key']
        app.config['GOOGLE_SEC'] = dict_obj['google_sec']
        app.config['YOUTUBE_API_KEY'] = dict_obj['youtube_api_key']
        ps_user = dict_obj['ps_user']
        ps_pass = dict_obj['ps_pass']
        ps_db = dict_obj['ps_db']
        ps_server = dict_obj['ps_server']
        db_conn_str = f'{ps_user}:{ps_pass}@{ps_server}:5432/{ps_db}'
        app.config['PG_CONNECTION_STRING'] = f"postgresql+psycopg://{db_conn_str}"
        app.config['PG_TORTOISE_CONNECTION_STRING'] = f"postgres://{db_conn_str}"
    except Exception as e:
        raise Exception(e)