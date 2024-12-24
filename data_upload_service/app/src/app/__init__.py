import time
from typing import List

from .routes import register_routes

from .load_creds import quart_app_creds_load
from quart import Quart
from quart_cors import cors
from quart_schema import QuartSchema, RequestSchemaValidationError, ResponseSchemaValidationError
from .set_logger import logger_set
from tortoise.transactions import  in_transaction
from data_models.datasource_model import DataFeed
from data_models.bot_model import DataSource
from tortoise import Tortoise

from .data_upload.models.datafeed_postgres_model import DataFeedPostgres
from .database import init_pgvector, init_quart_app_db, init_tortoise
from .data_upload.services.data_upload_service import data_upload
from .config import Config, Development
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from tortoise.query_utils import Prefetch
from quart_jwt_extended import (
    JWTManager
)

async def start_consumer(config: Config):
    
    logger_set(config=config)
    
    pg_async_engine: AsyncEngine | None = None
    
    try:
        pg_async_engine = create_async_engine(config.PG_CONNECTION_STRING, echo=False)
        init_pgvector(config=config)
        await init_tortoise(config=config)
        datafeeds:List[DataFeed] = []
        datasource_prefetch = Prefetch('datasource', queryset=DataSource.all().only('datasource_id', 'datasource_name'))
        msg: DataFeedPostgres
        while True:
            async with in_transaction() as connection:
                datafeeds = await DataFeed.filter(datafeedloadstatus_id='NEW').only('datafeed_id',
                                                        'datafeed_name',
                                                        'datafeed_source_unique_id',
                                                        'datafeed_source_title',
                                                        'datafeedsource_config_cipher',
                                                        'kdf_salt',
                                                        'nonce',
                                                        'auth_tag',
                                                        'datafeedsource_id',
                                                        'datasource_id',
                                                        'modified').order_by('modified').prefetch_related(datasource_prefetch)
                print('connected')
                if len(datafeeds) == 0:
                    time.sleep(30)
                else:
                    await DataFeed.filter(datafeedloadstatus_id='NEW').update(datafeedloadstatus_id='LOADING')
            for df in datafeeds:
                datafeedsource_id = df.datafeedsource_id # type: ignore
                msg = DataFeedPostgres(datafeedsource_id=datafeedsource_id, 
                                    datafeed_source_unique_id=df.datafeed_source_unique_id,
                                    datafeed_id=df.datafeed_id,
                                    datafeed_source_title=df.datafeed_source_title,
                                    datasource_id=df.datasource.datasource_id,
                                    datasource_name=df.datasource.datasource_name,
                                    )
                if df.kdf_salt and df.datafeedsource_config_cipher and df.nonce and df.auth_tag:
                    msg.kdf_salt = df.kdf_salt.hex()
                    msg.ciphertext = df.datafeedsource_config_cipher.hex()
                    msg.nonce = df.nonce.hex()
                    msg.auth_tag = df.auth_tag.hex()
                    
                await data_upload(config=config, 
                                    datafeed_msg=msg, 
                                    pg_async_engine=pg_async_engine
                                    )
                """
                await data_upload(config=config, 
                                    msg='msg.value.decode()', 
                                    pg_async_engine=pg_async_engine
                                    )
                print (df.datasource.datasource_name)
                """
    except KeyboardInterrupt:
        print('Exiting gracefully...')
        if pg_async_engine:
            await pg_async_engine.dispose()
        await Tortoise.close_connections()
    except Exception as e:
        if pg_async_engine:
            await pg_async_engine.dispose()
        await Tortoise.close_connections()
        logging.error(e.__str__())
    finally:
        if pg_async_engine:
            await pg_async_engine.dispose()
        await Tortoise.close_connections()
            
        
def create_quart_app(app_config: Config):
    """In production create as app = create_app('Production')"""
    app = Quart(__name__)
    QuartSchema(app, openapi_path = "/dataupload/openapi.json",
                redoc_ui_path = "/apdatauploadi/redocs",
                scalar_ui_path  = "/dataupload/scalar",
                swagger_ui_path = "/dataupload/docs")
    @app.errorhandler(RequestSchemaValidationError)
    async def handle_request_validation_error(error):
        logging.error(f'quart schema request validation error: {str(error.validation_error)}')   
        return {
      "error": 'All required fields are not provided',
     }, 400
    
    @app.errorhandler(ResponseSchemaValidationError)
    async def handle_response_validation_error(error):
        logging.error(f'quart schema response validation error: {str(error.validation_error)}')   
        return {
      "error": 'Response validation failed',
     }, 500
    app = cors(app, allow_origin="*")
    app.config['APP_ROOT_LOGGER']  = logger_set(config=app_config)
    app.config.from_object(app_config)
    quart_app_creds_load(app)

    init_quart_app_db(app=app, generate_schemas=True)
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1024
    app.config['CONFIG'] = app_config 
    @app.before_serving
    async def create_pg_async_engine():
        print('before serving')
        engine = create_async_engine(app.config['PG_CONNECTION_STRING'], echo=False)
        app.config['PG_ASYNC_ENGINE'] = engine
    
    @app.after_serving
    async def clean_up():
        print('aftr serving')
        engine: AsyncEngine = app.config['PG_ASYNC_ENGINE']
        await engine.dispose()
        
    register_routes(app)
    JWTManager(app)
    return app