from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class LlmConfig(BaseModel):
    url: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=256)
    api_key: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=512)
    api_key_header: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=64)
    user_name: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=64)
    password: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=32)
    
class BotUserLlm(BaseModel):
    bot_id: int
    user_llm_id:int
    llm_name: str
    llmmodeltype_name: str
    llm_config: LlmConfig
    datasource_id: Optional[int] = None
    datasource_name: Optional[str] = None