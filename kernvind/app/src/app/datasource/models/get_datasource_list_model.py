from datetime import datetime
from typing import Optional
from ...core.models.model_validators import remove_whitespaces
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel

class DataSourceList(BaseModel):
    datasource_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    datasource_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=1024)
    datasource_id: int
    created_by_user_id: int
    created: datetime
    modified: datetime