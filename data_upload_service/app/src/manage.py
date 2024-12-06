import asyncio
from app.config import Development, Production
from app import start_consumer
from app.load_creds import creds_load

def dev_app():
    config=Development()
    creds_load(config=config)
    asyncio.run(start_consumer(config=config))
    
def prod_app():
    config=Production()
    creds_load(config=config)
    asyncio.run(start_consumer(config=config))

if __name__ == '__main__':
    prod_app()