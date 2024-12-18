
import datetime
from logging import Logger
import os
from typing import Optional

from langchain_huggingface import HuggingFaceEmbeddings

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    HOST = '0.0.0.0'
    PORT = 5001
    PGVECTOR_LOGGER: Logger
    APP_LOG_HANDLER: Logger
    PG_CONNECTION_STRING: str
    PG_TORTOISE_CONNECTION_STRING: str
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    EMBEDDINGS_LENGTH=384
    GOOGLE_SEC: str
    PROXY: Optional[str] = None
    PROXY_AUTH: Optional[str] = None
    JWT_ACCESS_TOKEN_EXPIRES=datetime.timedelta(minutes=10)
    JWT_ALGORITHM = 'RS256'
    SSH_KEY_PATH_TUNNEL = '/ssh_key/Ec2SSH.pem'
    LOGDIR = './logs'
    TUNNEL_BIND_LOCAL_PORT = 5011
    SSH_USER = 'ec2-user'
    PROD_CREDS_FILE_PATH = ''
    DEV_CREDS_FILE_PATH = '../../sec/app_creds_dev_host.json'
    AWS_CLOUDWATCH_LOG_GROUP = ''
    AWS_CLOUDWATCH_LOG_STREAM = ''
    APP_LOGGER = 'data_upload'
    AWS_CLOUDWATCH_LOG_RETENTION_DAYS = 180

class Development(Config):
    DEBUG = True
class Production(Config):
    AWS_CLOUDWATCH_LOG_STREAM = 'data_upload_service'
    AWS_CLOUDWATCH_LOG_GROUP = 'prod_data_uplaod'
    SECRET_KEY = 'an actually secret key'
class ProductionLocal(Config):
    AWS_CLOUDWATCH_LOG_STREAM = 'data_upload_service'
    AWS_CLOUDWATCH_LOG_GROUP = 'prod_data_uplaod'
    SSH_KEY_PATH_TUNNEL = os.path.abspath('../../sec/ssh_key/Ec2SSH.pem')
    PROD_CREDS_FILE_PATH = '../../sec/prod_creds_local_host.json'
    LOGDIR = './logs'
class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

