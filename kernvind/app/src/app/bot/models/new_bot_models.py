from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class BotIn(BaseModel):
    bot_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    bot_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5,
                                                                                           max_length=1024)
    created_by_user_id: int
    user_llm_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=50)
    user_llm_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=512)
    user_llm_id: int
    llm_name:str
    llm_type_name: str
    created_by_name: str
    datasource_id: Optional[int] = None
    datasource_name: Optional[str] = None
    can_add_users: bool = False
    can_change_datasource: bool = False
    can_see_datasource: bool = False
    can_see_datasourcefeed: bool = False
    can_change_datasourcefeed: bool = False
    can_see_llm: bool = False
    can_change_llm: bool = False


class BotOut(BotIn):
    bot_id: int
    created: datetime
    modified: datetime

