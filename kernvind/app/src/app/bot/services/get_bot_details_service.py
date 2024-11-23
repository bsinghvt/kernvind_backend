import logging
from typing import List, Optional, cast
from data_models.bot_model import Bot, BotUserXref
from data_models.user_model import User, UserLlm
from tortoise.query_utils import Prefetch

from ..models.bot_details_model import BotDetails, BotUsers

from ..models.get_bot_list_model import GetBot
from ...core.models.error_model import Failure


async def get_bot_details(bot_id:int, user_id: int):
    user_llm_prefetch =  Prefetch('user_llm', queryset=UserLlm.all().only('user_llm_id','llm_id','user_llm_description','user_llm_name').prefetch_related('llm'))
    created_by_user_prefetch = Prefetch('created_by_user', queryset=User.all().only('full_name', 'user_id','email'))
    users_prefetch = Prefetch('user', queryset=User.all().only('full_name', 'user_id','email'))
    try:
        botxrefs =  await BotUserXref.filter(user_id=user_id, bot_id=bot_id).prefetch_related(
            Prefetch('bot', queryset=Bot.all().prefetch_related(
                'datasource', 
                user_llm_prefetch,
                created_by_user_prefetch
                ) 
            )
        )
        if len(botxrefs) == 0 or len(botxrefs) > 1:
            logging.error(f'Bot {bot_id} is unauthorized')
            return Failure(error="Unauthorized bot."), 401
        user: User
        bot: Bot
        botxref = botxrefs[0]
        user =  cast(User, botxref.bot.created_by_user)
        is_owner = False
        if user.user_id == user_id:
            is_owner = True
        bot = cast(Bot, botxref.bot)
        datasource_id = None
        datasource_name = None
        datasource_desc = None
        if bot.datasource and botxref.can_see_datasource:
            datasource_id = bot.datasource.datasource_id
            datasource_name = bot.datasource.datasource_name
            datasource_desc = bot.datasource.datasource_description
        user_llm_id = None
        llm_name = None
        llm_type_name = None
        user_llm_name: Optional[str] = None
        user_llm_desc = None
        if botxref.can_see_llm:
            user_llm_id = bot.user_llm.user_llm_id
            llm_name = bot.user_llm.llm_id
            llm_type_name = bot.user_llm.llm.llmmodeltype_id
            user_llm_desc = bot.user_llm.user_llm_description
            user_llm_name = bot.user_llm.user_llm_name
            
        bot_details = GetBot(bot_id=bot.bot_id,
                                    user_llm_name=user_llm_name,
                                    user_llm_description=user_llm_desc,
                                    user_llm_id=user_llm_id,
                                    can_see_llm=botxref.can_see_llm,
                                    llm_name=llm_name,
                                    llm_type_name=llm_type_name,
                                    bot_name=bot.bot_name,
                                    can_add_users=botxref.can_add_users,
                                    can_change_datasource=botxref.can_change_datasource,
                                    can_change_datasourcefeed=botxref.can_change_datasourcefeed,
                                    can_change_llm=botxref.can_change_llm,
                                    can_see_datasource=botxref.can_see_datasource,
                                    can_see_datasourcefeed=botxref.can_see_datasourcefeed,
                                    bot_description=bot.bot_description,
                                    created_by_user_id=user.user_id,
                                    is_owner=is_owner,
                                    created_by_name=user.full_name,
                                    datasource_id=datasource_id,
                                    datasource_name=datasource_name,
                                    datasource_description = datasource_desc,
                                    created=bot.created,
                                    modified=bot.modified)

        botxrefs =  await BotUserXref.filter(bot_id=bot_id).prefetch_related(
            users_prefetch,
        )
        
            
        bot_users: List[BotUsers] = []
        for user_details in botxrefs:
            user =  cast(User, user_details.user)
            if user.user_id != user_id:
                bot_users.append(BotUsers(user_id=user.user_id, full_name=user.full_name, email=user.email
                                    ))
        return BotDetails(users=bot_users,bot=bot_details) 
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500