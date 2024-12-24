from .config import Config

from .set_logger import logger_set

from .load_creds import creds_load
from .initial_database_data import loadInitialDatabaseData
from .database import init_db
from quart import Quart
from quart_schema import QuartSchema
from quart_schema import RequestSchemaValidationError, ResponseSchemaValidationError

from .extensions import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from quart_jwt_extended import (
    JWTManager
)
import logging
from .routes import register_routes
from quart_cors import cors

def create_app(app_config: Config) -> Quart:
    """In production create as app = create_app('Production')"""
    app = Quart(__name__)
    QuartSchema(app, openapi_path = "/api/openapi.json",
                redoc_ui_path = "/api/redocs",
                scalar_ui_path  = "/api/scalar",
                swagger_ui_path = "/api/docs")
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
    creds_load(app)
    print(app.config['PG_CONNECTION_STRING'])
    init_db(app=app, generate_schemas=True)
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1024
    @app.before_serving
    async def start_up():
        import os
        print('serv')
        engine = create_async_engine(app.config['PG_CONNECTION_STRING'], echo=False)
        app.config['PG_ASYNC_ENGINE'] = engine
        await loadInitialDatabaseData()
        

    @app.after_serving
    async def clean_up():
        print('aftr serving')
        engine: AsyncEngine = app.config['PG_ASYNC_ENGINE']
        await engine.dispose()
    register_routes(app)
    JWTManager(app)
    bcrypt.init_app(app)
    return app