from datetime import datetime
from typing import Optional
from ...core.models.model_validators import remove_whitespaces
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel

class GetBot(BaseModel):
    bot_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    bot_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5,
                                                                                        max_length=1024)
    created_by_user_id: int
    is_owner: Optional[bool] = None
    user_llm_id: Optional[int] = None
    user_llm_name: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=50)
    user_llm_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=512)
    llm_name: Optional[str] = None
    llm_type_name: Optional[str] = None
    created_by_name: str
    datasource_id: Optional[int] = None
    datasource_name: Optional[str] = None
    datasource_description: Optional[str] = None
    can_add_users: bool = False
    can_change_datasource: bool = False
    can_see_datasource: bool = False
    can_see_datasourcefeed: bool = False
    can_change_datasourcefeed: bool = False
    can_see_llm: bool = False
    can_change_llm: bool = False
    bot_id: int
    created: datetime
    modified: datetime
