from typing import Optional
from pydantic import BaseModel

class DataFeedApacheKafka(BaseModel):
    datafeed_source_unique_id: str
    datasource_name: str
    datafeedsource_id: str
    datafeed_source_unique_id: str
    datafeed_source_title: str
    datasource_id: int
    datafeed_id: int
    kdf_salt: Optional[str] = None
    ciphertext: Optional[str] = None
    nonce: Optional[str] = None
    auth_tag: Optional[str] = None