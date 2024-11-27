
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
    PG_CONNECTION_STRING: str
    PG_TORTOISE_CONNECTION_STRING: str
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-mpnet-base-v2')
    EMBEDDINGS_LENGTH=768
    GOOGLE_SEC: str
class Development(Config):
    DEBUG = True
class Production(Config):
    SECRET_KEY = 'an actually secret key'
class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

