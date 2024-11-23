from pydantic import BaseModel
class MetaData(BaseModel):
    source_id: str
    source_title: str
    datafeedsource_id: str
    datasource_id: int
    datafeed_id: int