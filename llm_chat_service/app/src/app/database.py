from quart import Quart
from tortoise.contrib.quart import register_tortoise
from tortoise.exceptions import ConfigurationError


def init_db(app: Quart, generate_schemas=False):
   try:
       register_tortoise(
           app,
           db_url=app.config['PG_TORTOISE_CONNECTION_STRING'],
           #db_url="postgres://bitziv_user:S3cret@localhost:5432/bitziv_db",
           modules={"models": ["data_models.user_model",
                                "data_models.bot_model",
                               "data_models.llm_model",
                                 "data_models.datasource_model",
                               "data_models.datafeed_source_model",
                               "data_models.chat_message_model",
                               "data_models.vector_model",
                             ]},
           generate_schemas=generate_schemas,
           )
   except ConfigurationError as err:
       raise
       
