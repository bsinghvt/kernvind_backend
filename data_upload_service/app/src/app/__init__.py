import os
import time
from typing import List
from tortoise.transactions import  in_transaction
from data_models.datasource_model import DataFeed
from data_models.bot_model import DataSource
from tortoise import Tortoise

from .data_upload.models.datafeed_postgres_model import DataFeedPostgres
from .database import init_pgvector, init_tortoise
from .data_upload.services.data_upload_service import data_upload
from .config import Config
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from tortoise.query_utils import Prefetch

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

pgvector_logger = logging.getLogger('pgvector_logger')
handler = RotatingFileHandler('/logs/pgvector_logger.warn', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s-%(lineno)d-%(message)s')
handler.setFormatter(formatter)
pgvector_logger.addHandler(handler)

async def start_consumer(config: Config):
    pg_async_engine: AsyncEngine | None = None
    try:
        config.PGVECTOR_LOGGER = pgvector_logger
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
            
        
        