import asyncio
from app.config import Development, Production, ProductionLocal
from app import create_quart_app, start_consumer
from app.load_creds import creds_load
from app.prod_local_creds_load import prod_local_creds_load

def dev_app():
    config=Development()
    creds_load(config=config)
    asyncio.run(start_consumer(config=config))

def prod_local_app_in_docker():
    config=Development()
    prod_local_creds_load(config=config)
    asyncio.run(start_consumer(config=config))

def prod_local_app_in_host():
    config=ProductionLocal()
    prod_local_creds_load(config=config)
    asyncio.run(start_consumer(config=config))
    
def prod_app():
    config=Production()
    creds_load(config=config)
    asyncio.run(start_consumer(config=config))
    
def quart_dev_app():
    config=Development()
    app = create_quart_app(app_config=config)
    app.run(host=app.config['HOST'], port=app.config['PORT'])

if __name__ == '__main__':
    prod_app()