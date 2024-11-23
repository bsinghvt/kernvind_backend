from typing import List, Optional
from pydantic import BaseModel

from .user_llm_model import UserLlmOut

class UserLlmBotOut(BaseModel):
    bot_id: int
    bot_name: str
    bot_description: Optional[str] = None
    
class UserLlmDetails(BaseModel):
    user_llm: UserLlmOut
    user_llm_bots: List[UserLlmBotOut]