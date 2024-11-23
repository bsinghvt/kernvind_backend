import logging

from data_models.bot_model import BotUserXref

from tortoise.exceptions import IntegrityError

from data_models.user_model import User

from ..models.bot_add_user_model import BotAddUser
from .get_bot_details_service import get_bot_details

from ...core.models.error_model import Failure


async def bot_add_user(user_id:int, bot_new_user: BotAddUser):
    try:
        bot_id = bot_new_user.bot_id
        user_to_add_email = bot_new_user.user_to_add_email
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id, can_add_users=True)
        if len(botxrefs) == 0:
            return Failure(error="User is Unauthorized to add user to bot"), 401
        if len(botxrefs) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        user = await User.filter(email=user_to_add_email).only('user_id')
        if len(user) == 0:
            return Failure(error=f"User with {user_to_add_email} doesn't exist, please ask user to resgister"), 401
        if len(user) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        
        user_to_add_id = user[0].user_id
        await BotUserXref.create(user_id = user_to_add_id, 
                                    bot_id = bot_id, 
                                    added_by_user_id = user_id,
                                    can_add_users=bot_new_user.can_add_users,
                                    can_change_datasource=bot_new_user.can_change_datasource,   
                                    can_change_llm=bot_new_user.can_change_llm,
                                    can_change_datasourcefeed=bot_new_user.can_change_datasourcefeed,
                                    can_see_datasource=bot_new_user.can_see_datasource,
                                    can_see_datasourcefeed=bot_new_user.can_see_datasourcefeed,
                                    can_see_llm=bot_new_user.can_see_llm)
        return await get_bot_details(bot_id=bot_id, user_id=user_id)
    except IntegrityError as ie:
        err = ie.__str__()
        logging.error(f'{ie.__str__()}')
        if 'duplicate key' in err:
            return Failure(error="user already exists in bot"), 409
        return Failure(error="Something went wrong. Please try again"), 500
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500