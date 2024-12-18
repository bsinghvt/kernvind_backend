from typing import Optional
from pydantic import BaseModel

class LlmConfig(BaseModel):
    llm_name: Optional[str] = None
    llm_type: Optional[str] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: Optional[str] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    use_my_llm: bool = False
    
class PlaygroundChatMessage(BaseModel):
    message_id: Optional[str] = None
    message_user_name: Optional[str] = None
    bot_id: str
    first_message: Optional[bool] = False
    message_text: str
    llm_config: Optional[LlmConfig] = None
    