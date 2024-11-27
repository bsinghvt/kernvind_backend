import asyncio
import os
from app.config import Development
from app import start_consumer
from app.load_creds import creds_load

def dev_app():
    config=Development()
    creds_load(config=config)
    asyncio.run(start_consumer(config=config))
    
    #init_db(app=app, generate_schemas=True)