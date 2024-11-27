import os

from .load_creds import creds_load
from .initial_database_data import loadInitialDatabaseData
from .database import init_db
from quart import Quart
from quart_schema import QuartSchema
from quart_schema import RequestSchemaValidationError, ResponseSchemaValidationError

from .extensions import bcrypt
#from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from quart_jwt_extended import (
    JWTManager
)
import logging
from logging.handlers import RotatingFileHandler
from .routes import register_routes
from quart_cors import cors

if not os.path.exists('/logs'):
    os.makedirs('/logs')
root = logging.getLogger()
handler = RotatingFileHandler('/logs/log.error', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s-%(lineno)d-%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

handler = RotatingFileHandler('/logs/log.info', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

root.addHandler(handler)
root.setLevel(logging.INFO)

def create_app(mode='Development'):
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
    app.config.from_object(f'config.{mode}')
    app.config['APP_ROOT_LOGGER'] = root
    creds_load(app)
    init_db(app=app, generate_schemas=True)
    """
    @app.before_serving
    async def create_pg_async_engine():
        print('before serving')
        engine = create_async_engine(app.config['PG_CONNECTION_STRING'], echo=True)
        app.config['PG_ASYNC_ENGINE'] = engine
    """
    @app.before_serving
    async def start_up():
        import os
        print('serv')
        await loadInitialDatabaseData()
        
    """
    @app.after_serving
    async def clean_up():
        print('aftr serving')
        engine: AsyncEngine = app.config['PG_ASYNC_ENGINE']
        await engine.dispose()
    """  
    register_routes(app)
    JWTManager(app)
    bcrypt.init_app(app)
    return app