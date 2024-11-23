from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ChatMessageIn(BaseModel):
    chat_message_id: Optional[int] = None
    bot_id: int
    notification: Optional[bool] = False
    user_id_in: int
    message_text: str
    
class ChatMessageOut(ChatMessageIn):
    message_id: str
    created: datetime
    modified: datetime
    user_id_out: Optional[int] = None
    message_user_name: Optional[str] = None
    
class ChatMessageDatabase(BaseModel):
    user_message: str
    notification: Optional[bool] = None
    llm: str
    datasource_id: Optional[int] = None
    bot_answer: Optional[str] = None
    bot_id:int
    user_id:int