from pydantic import BaseModel

class BotChangeLlm(BaseModel):
    bot_id: int
    user_llm_id: int