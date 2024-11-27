import logging
from logging.handlers import RotatingFileHandler
import os
from quart import Quart
from quart_schema import QuartSchema
from quart_jwt_extended import (
    JWTManager
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from .load_creds import creds_load
from .database import init_db
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

from app.routes import register_routes
def create_app(mode='Development'):
    """In production create as app = create_app('Production')"""
    app = Quart(__name__)
    QuartSchema(app)
    app.config.from_object(f'config.{mode}')
    creds_load(app)
    init_db(app=app, generate_schemas=True)
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
        
    JWTManager(app)
    register_routes(app)
    return app