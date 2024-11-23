import logging
from ..models.new_bot_models import BotIn, BotOut
from ...core.models.error_model import Failure
from data_models.bot_model import Bot, BotUserXref
from tortoise.exceptions import IntegrityError
from tortoise.transactions import  in_transaction


async def create_bot(bot_in: BotIn):
    try:
        async with in_transaction() as connection:
            new_bot = await Bot.create(bot_name=bot_in.bot_name, 
                                       bot_description=bot_in.bot_description,
                                       user_llm_id=bot_in.user_llm_id,
                                       created_by_user_id=bot_in.created_by_user_id,
                                       datasource_id=bot_in.datasource_id)
            await BotUserXref.create(user_id = bot_in.created_by_user_id, 
                                     bot_id = new_bot.bot_id, 
                                     added_by_user_id = bot_in.created_by_user_id,
                                     can_add_users=True,
                                     can_change_datasource=True,    
                                     can_change_llm=True,
                                     can_change_datasourcefeed=True,
                                     can_see_datasource=True,
                                     can_see_datasourcefeed=True,
                                    can_see_llm=True)
            logging.info(f'{bot_in.bot_name} created successfully by user {bot_in.created_by_user_id}, {bot_in.created_by_name}')
            return BotOut(bot_id=new_bot.bot_id,
                      bot_name=new_bot.bot_name,
                      bot_description=new_bot.bot_description,
                      created_by_user_id=bot_in.created_by_user_id,
                      user_llm_id=bot_in.user_llm_id,
                      user_llm_name=bot_in.user_llm_name,
                      user_llm_description=bot_in.user_llm_description,
                      llm_name=bot_in.llm_name,
                      llm_type_name=bot_in.llm_type_name,
                      created_by_name=bot_in.created_by_name,
                      datasource_id=bot_in.datasource_id,
                      datasource_name=bot_in.datasource_name,
                      can_change_datasource=True,
                      can_add_users=True,
                      can_change_llm=True,
                      can_change_datasourcefeed=True,
                      can_see_datasource=True,
                      can_see_datasourcefeed=True,
                      can_see_llm=True,
                      created=new_bot.created,
                      modified=new_bot.modified,
                      ), 201
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'duplicate key' in err:
            return Failure(error="bot name already exists"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong. Please try again"), 500
