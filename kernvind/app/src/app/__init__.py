from .initial_database_data import loadInitialDatabaseData
from .database import init_db
from quart import Quart
from quart_schema import QuartSchema


from .extensions import bcrypt
#from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from quart_jwt_extended import (
    JWTManager
)
import logging
from logging.handlers import RotatingFileHandler
from .routes import register_routes
from quart_cors import cors

root = logging.getLogger()
handler = RotatingFileHandler('log.error', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s-%(lineno)d-%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

handler = RotatingFileHandler('log.info', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

root.addHandler(handler)
root.setLevel(logging.INFO)

def create_app(mode='Development'):
    """In production create as app = create_app('Production')"""
    app = Quart(__name__)
    QuartSchema(app)
    app = cors(app, allow_origin="*")
    app.config.from_object(f'config.{mode}')
    app.config['APP_ROOT_LOGGER'] = root
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
        google_sec_file = os.getenv('GOOGLE_SEC_FILE')
        if not google_sec_file:
            raise Exception('Error with google drive auth')
        with open(google_sec_file, 'r') as reader:
            app.config['GOOGLE_SEC'] = reader.read()
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