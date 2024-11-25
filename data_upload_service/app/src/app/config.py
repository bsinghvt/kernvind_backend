
import datetime
from logging import Logger
import os

from langchain_huggingface import HuggingFaceEmbeddings

class Config():
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    HOST = '0.0.0.0'
    PORT = 5001
    PGVECTOR_LOGGER: Logger
    PG_CONNECTION_STRING = "postgresql+psycopg://bitziv_user:S3cret@postgres:5432/bitziv_db"
    PG_TORTOISE_CONNECTION_STRING = "postgres://bitziv_user:S3cret@postgres:5432/bitziv_db"
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-mpnet-base-v2')
    EMBEDDINGS_LENGTH=768
class Development(Config):
    DEBUG = True

PS_USER = os.getenv('PS_USER')
PS_PASS = os.getenv('PS_PASS')
PS_DB = os.getenv('PS_DB')
PS_SERVER = os.getenv('PS_SERVER')
class Production(Config):
    BOT_CHAT_USER_REMOVE_URL = ''
    SECRET_KEY = 'an actually secret key'
    PG_CONNECTION_STRING = f"postgresql+psycopg://{PS_USER}:{PS_PASS}@{PS_SERVER}:5432/{PS_DB}"
    PG_TORTOISE_CONNECTION_STRING = f"postgres://{PS_USER}:{PS_PASS}@{PS_SERVER}:5432/{PS_DB}"

class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

