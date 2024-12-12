import os
import json
from sshtunnel import SSHTunnelForwarder
from .config import Config

def prod_local_creds_load(config: Config):
    app_creds_file = os.getenv('PROD_APP_CREDS_JSON_FILE')
    app_creds = os.getenv('APP_CREDS_JSON')
    json_str: str
    if app_creds_file:
        with open(app_creds_file, 'r') as reader:
            json_str = reader.read()
    elif app_creds:
        json_str = app_creds
    elif os.path.exists(config.PROD_CREDS_FILE_PATH):
        with open(config.PROD_CREDS_FILE_PATH, 'r') as reader:
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
        ssh_host = dict_obj['ssh_host']
        
        tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=config.SSH_USER,
            ssh_private_key=config.SSH_KEY_PATH_TUNNEL,
            remote_bind_address=(ps_server, 5432),
            local_bind_address=('localhost',config.TUNNEL_BIND_LOCAL_PORT), # could be any available port
        )
        tunnel.start()     
        db_conn_str = f'{ps_user}:{ps_pass}@localhost:{config.TUNNEL_BIND_LOCAL_PORT}/{ps_db}'
        config.PG_CONNECTION_STRING = f"postgresql+psycopg://{db_conn_str}"
        config.PG_TORTOISE_CONNECTION_STRING = f"postgres://{db_conn_str}"
    except Exception as e:
        raise Exception(e)