
from langchain_huggingface import HuggingFaceEmbeddings

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    HOST = '0.0.0.0'
    PORT = 5001
    LC_PG_VECTOR_INSTANCE_COLLECTION = {}
    LC_PG_VECTOR_INSTANCE_COLLECTION_FOR_BOT = {}
    LC_LLM_INSTANCE_COLLECTION_FOR_BOT = {}
    LC_LLM_INSTANCE_COLLECTION = {}
    LC_USER_LLM_NAME_INSTANCE_COLLECTION = {}
    PLAYGROUND_LLM_CONFIG_DICT = {}
    QUART_SCHEMA_PYDANTIC_DUMP_OPTIONS = {'exclude_none': True}
    JWT_ALGORITHM = 'RS256'
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    EMBEDDINGS_LENGTH=384
    JWT_DECODE_LEEWAY = 10
    JWT_ERROR_MESSAGE_KEY = 'error'


class Development(Config):
    DEBUG = True

class Production(Config):
    BOT_CHAT_USER_REMOVE_URL = ''
    SECRET_KEY = 'an actually secret key'
class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

