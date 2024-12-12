
import datetime
from logging import Logger
import os
from typing import Optional

from langchain_huggingface import HuggingFaceEmbeddings

class Config():
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    HOST = '0.0.0.0'
    PORT = 5001
    PGVECTOR_LOGGER: Logger
    PG_CONNECTION_STRING: str
    PG_TORTOISE_CONNECTION_STRING: str
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-mpnet-base-v2')
    EMBEDDINGS_LENGTH=768
    GOOGLE_SEC: str
    PROXY: Optional[str] = None
    PROXY_AUTH: Optional[str] = None
    SSH_KEY_PATH_TUNNEL = '/ssh_key/Ec2SSH.pem'
    LOGDIR = '/log'
    TUNNEL_BIND_LOCAL_PORT = 5011
    SSH_USER = 'ec2-user'
    PROD_CREDS_FILE_PATH = ''

class Development(Config):
    DEBUG = True
class Production(Config):
    SECRET_KEY = 'an actually secret key'
class ProductionLocal(Config):
    SSH_KEY_PATH_TUNNEL = os.path.abspath('../../sec/ssh_key/Ec2SSH.pem')
    PROD_CREDS_FILE_PATH = '../../sec/prod_creds_local_host.json'
    LOGDIR = './logs'
class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

