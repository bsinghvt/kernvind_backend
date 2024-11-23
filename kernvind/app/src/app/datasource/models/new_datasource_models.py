from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from quart_schema.pydantic import File
from pydantic import BeforeValidator, Field, BaseModel
from ...core.models.model_validators import remove_whitespaces


class DataSourceFeed(BaseModel):
    datafeed_id: Optional[int] = None
    datafeed_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    datafeed_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=1024)
    datafeedsource_id: str
    created_by_name: str
    created_by_user_id: int
    datafeed_source_unique_id: str
    datafeedloadstatus_id: Optional[str] = None
    access_key: Optional[str] = None
    datafeed_source_title: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=1, max_length=512)
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    
class DataSourceIn(BaseModel):
    datasource_name: Annotated[str, BeforeValidator(remove_whitespaces)] = Field(min_length=5, max_length=64)
    datasource_description: Annotated[Optional[str], BeforeValidator(remove_whitespaces)] = Field(default=None, min_length=5, max_length=1024)
    created_by_user_id: int
    created_by_name: str
    datasource_feed: DataSourceFeed
    file: Optional[File] = None

class DataSourceOut(DataSourceIn):
    datasource_id: int
    created: datetime
    modified: datetime

class Upload(BaseModel):
    file: Optional[File] = None
    
    

    
    

