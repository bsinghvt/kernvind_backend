from .set_logger import logger_set
from quart import  Quart
from quart_schema import QuartSchema
from quart_jwt_extended import (
    JWTManager
)
from .config import Config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from .load_creds import creds_load
from .database import init_db

from app.routes import register_routes
def create_app(app_config: Config):
    """In production create as app = create_app('Production')"""
    app = Quart(__name__)
    QuartSchema(app)
    app.config['APP_ROOT_LOGGER']  = logger_set(config=app_config)
    app.config.from_object(app_config)
    if app.config.get('TESTING', False) == False:
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