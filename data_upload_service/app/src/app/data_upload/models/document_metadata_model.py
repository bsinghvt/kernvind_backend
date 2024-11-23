from typing import Optional
from pydantic import BaseModel
class MetaData(BaseModel):
    source_id: str
    source_title: str
    page_name: Optional[str] = None
    page_number: Optional[str] = None
    datafeedsource_id: str
    datasource_id: int
    datafeed_id: int