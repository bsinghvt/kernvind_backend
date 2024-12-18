from tortoise import Tortoise
from sqlalchemy import create_engine
from tortoise.exceptions import ConfigurationError
from langchain_postgres import PGVector
from .config import Config

def init_pgvector(config: Config):
    try:
        embeddings = config.EMBEDDINGS
        engine = create_engine(config.PG_CONNECTION_STRING, echo=False)
        PGVector(
            embeddings=embeddings,
            embedding_length=config.EMBEDDINGS_LENGTH,
            collection_name='ZZZZZTTTTTEEEESSSSTT',
            connection=engine,
            use_jsonb=True,
            async_mode=False,
            logger=config.PGVECTOR_LOGGER
        )
    except Exception as err:
        raise

async def init_tortoise(config: Config):
    try:
        await Tortoise.init(
            db_url=config.PG_TORTOISE_CONNECTION_STRING,
            #db_url="postgres://bitziv_user:S3cret@localhost:5432/bitziv_db",
            modules={"models": [
                                "data_models.user_model",
                                "data_models.bot_model",
                                "data_models.llm_model",
                                "data_models.datasource_model",
                                "data_models.datafeed_source_model",
                                "data_models.vector_model",
                            ]},
            )
        await Tortoise.generate_schemas()
    except ConfigurationError as err:
        raise
    except Exception as err:
        raise
    

from quart import Quart
from tortoise.contrib.quart import register_tortoise
from tortoise.exceptions import ConfigurationError
from langchain_postgres import PGVector
from sqlalchemy import create_engine

def init_quart_app_db(app: Quart, generate_schemas=False):
  
  try:
    engine = create_engine(app.config['PG_CONNECTION_STRING'], echo=False)
    embeddings = app.config['EMBEDDINGS']
    embedding_length = app.config['EMBEDDINGS_LENGTH']
    PGVector(
            embeddings=embeddings,
            embedding_length=embedding_length,
            collection_name='ZZZZZTTTTTEEEESSSSTT',
            connection=engine,
            use_jsonb=True,
            async_mode=False,
    )
    register_tortoise(
      app,
      db_url=app.config['PG_TORTOISE_CONNECTION_STRING'],
      #db_url="postgres://bitziv_user:S3cret@localhost:5432/bitziv_db",
      modules={"models": [
          "data_models.vector_model",
          ]},
              generate_schemas=generate_schemas,
            )
  except ConfigurationError as err:
    raise
  except Exception as e:
    raise
  
