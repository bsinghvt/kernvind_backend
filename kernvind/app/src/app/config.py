
import datetime
from logging import Logger

from langchain_huggingface import HuggingFaceEmbeddings


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret'
    HOST = '0.0.0.0'
    PORT = 5001
    BCRYPT_LOG_ROUNDS = 12
    BCRYPT_HASH_PREFIX = '2b'
    LOGDIR = './logs'
    PGVECTOR_LOGGER: Logger
    APP_LOG_HANDLER: Logger
    EMBEDDINGS = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    EMBEDDINGS_LENGTH=384
    GOOGLE_SIGN_IN_ANDROID_WEB_CLIENT_ID = '526432072855-08g564n8r6j6ifv6pfp492jit7sctq7v.apps.googleusercontent.com'
    GOOGLE_SIGN_IN_WEB_CLIENT_ID = '450752284339-ulgvunhkpo3k392irbe4e7ovko4gc4j8.apps.googleusercontent.com'
    GOOGLE_SIGN_IN_IOS_CLIENT_ID = '450752284339-agsh7dq7sed4jhom2785s1api6i43oki.apps.googleusercontent.com'
    GOOGLE_SIGN_IN_ANDROID_CLIENT_ID = '450752284339-3u1r6v2c61iuo9saao7flgm43ga80rc7.apps.googleusercontent.com'
    BCRYPT_HANDLE_LONG_PASSWORDS = False
    QUART_SCHEMA_PYDANTIC_DUMP_OPTIONS = {'exclude_none': True}
    JWT_ALGORITHM = 'RS256'
    JWT_ACCESS_TOKEN_EXPIRES=datetime.timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES=datetime.timedelta(days=180)
    BOT_CHAT_USER_REMOVE_URL = 'http://llm_chat_service-llm_chat-service-dev-1:5001/chat/user'
    JWT_DECODE_LEEWAY = 10
    JWT_ERROR_MESSAGE_KEY = 'error'
    AWS_CLOUDWATCH_LOG_GROUP = ''
    AWS_CLOUDWATCH_LOG_STREAM = ''
    APP_LOGGER = 'kernvind_service'
    AWS_CLOUDWATCH_LOG_RETENTION_DAYS = 180
    AWS_REGION = 'us-east-1'


class Development(Config):
    DEBUG = True

class Production(Config):
    AWS_CLOUDWATCH_LOG_STREAM = 'api_kernvind_service'
    AWS_CLOUDWATCH_LOG_GROUP = 'api_kernvind_service'
    GOOGLE_SIGN_IN_ANDROID_WEB_CLIENT_ID = '450752284339-ulgvunhkpo3k392irbe4e7ovko4gc4j8.apps.googleusercontent.com'
    BOT_CHAT_USER_REMOVE_URL = 'https://api.kernvind.com/chat/user'
    SECRET_KEY = 'an actually secret key'
class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

