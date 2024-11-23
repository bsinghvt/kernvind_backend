from typing import Optional
from typing_extensions import Annotated
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces

class DataSourceAddFeed(BaseModel):
    datafeed_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    datafeed_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=1024)
    datafeedsource_id: str
    datasource_id: int
    datafeed_source_unique_id: str
    access_key: Optional[str] = None
    datafeed_source_title: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=1, max_length=512)