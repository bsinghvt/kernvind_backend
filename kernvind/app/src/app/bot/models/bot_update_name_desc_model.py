from typing import Optional
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class BotUpdateNameDescIn(BaseModel):
    bot_id: int
    bot_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    bot_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=1024)