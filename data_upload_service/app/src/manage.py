import asyncio
import os
from app.config import Development
from app import start_consumer

def dev_app():
    config=Development()
    google_sec_file = os.getenv('GOOGLE_SEC_FILE')
    google_sec = os.getenv('GOOGLE_SEC')
    if google_sec_file:
        with open(google_sec_file, 'r') as reader:
            config.GOOGLE_SEC = reader.read()
    elif google_sec:
        config.GOOGLE_SEC = google_sec
    else:
        raise Exception('Error with google drive auth')
    asyncio.run(start_consumer(config=config))
    
    #init_db(app=app, generate_schemas=True)