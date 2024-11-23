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

class UserLlmIn(BaseModel):
    llm_id: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=1, max_length=50)
    user_llm_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=50)
    user_llm_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=1, max_length=512)
    llm_type: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=1, max_length=50)
    llm_config: LlmConfig
    user_id: int


class UserLlmOut(UserLlmIn):
    user_llm_id: int
    created: datetime
    modified: datetime

class LlmListOut(BaseModel):
    llm_name: str
    llmmodeltype_name: str
    created: datetime
    modified: datetime

