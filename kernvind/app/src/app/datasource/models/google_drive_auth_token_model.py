
from datetime import datetime

from pydantic import BaseModel

    
class GoogleDriveAuthToken(BaseModel):
    token: str | None
    refresh_token: str | None
    token_uri: str | None
    universe_domain: str | None
    expiry:  datetime | None