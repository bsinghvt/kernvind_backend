import os
import json

from .config import Config

def creds_load(config: Config):
    app_creds_file = os.getenv('APP_CREDS_JSON_FILE')
    app_creds = os.getenv('APP_CREDS_JSON')
    json_str: str
    print(os.path.abspath(config.DEV_CREDS_FILE_PATH))
    if app_creds_file:
        with open(app_creds_file, 'r') as reader:
            json_str = reader.read()
    elif app_creds:
        json_str = app_creds
    elif os.path.exists(config.DEV_CREDS_FILE_PATH):
        with open(config.DEV_CREDS_FILE_PATH, 'r') as reader:
            json_str = reader.read()
    else:
        raise Exception('Error loading creds file')
    try:
        dict_obj = json.loads(json_str)
        config.GOOGLE_SEC = dict_obj['google_sec']
        ps_user = dict_obj['ps_user']
        ps_pass = dict_obj['ps_pass']
        ps_db = dict_obj['ps_db']
        ps_server = dict_obj['ps_server']
        if 'proxy' in dict_obj:
            proxy = dict_obj['proxy']
            proxy_auth = dict_obj['proxy_auth']
            config.PROXY = proxy
            config.PROXY_AUTH = proxy_auth
        db_conn_str = f'{ps_user}:{ps_pass}@{ps_server}:5432/{ps_db}'
        config.PG_CONNECTION_STRING = f"postgresql+psycopg://{db_conn_str}"
        config.PG_TORTOISE_CONNECTION_STRING = f"postgres://{db_conn_str}"
    except Exception as e:
        raise Exception(e)
    

import os
import json

def quart_app_creds_load(app):
    app_creds_file = os.getenv('APP_CREDS_JSON_FILE')
    app_creds = os.getenv('APP_CREDS_JSON')
    json_str: str
    creds_file_path = app.config['DEV_CREDS_FILE_PATH']
    print(os.path.abspath(creds_file_path))
    if app_creds_file:
        with open(app_creds_file, 'r') as reader:
            json_str = reader.read()
    elif app_creds:
        json_str = app_creds
    elif os.path.exists(creds_file_path):
        with open(creds_file_path, 'r') as reader:
            json_str = reader.read()
    else:
        raise Exception('Error loading creds file')
    try:
        dict_obj = json.loads(json_str)
        if 'proxy' in dict_obj:
            proxy = dict_obj['proxy']
            proxy_auth = dict_obj['proxy_auth']
            app.config['PROXY'] = proxy
            app.config['PROXY_AUTH'] = proxy_auth
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