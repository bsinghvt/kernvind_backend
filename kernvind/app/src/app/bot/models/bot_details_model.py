from typing import List

from .get_bot_list_model import GetBot

from pydantic import BaseModel

class BotUsers(BaseModel):
    user_id: int
    full_name: str
    email: str
    
class BotDetails(BaseModel):
    bot: GetBot
    users: List[BotUsers]