from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class BotAddUser(BaseModel):
    user_to_add_email: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    bot_id: int
    can_add_users: bool = False
    can_change_datasource: bool = False
    can_see_datasource: bool = False
    can_see_datasourcefeed: bool = False
    can_change_datasourcefeed: bool = False
    can_see_llm: bool = False
    can_change_llm: bool = False