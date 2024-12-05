import os
import json

from .config import Config

def creds_load(config: Config):
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