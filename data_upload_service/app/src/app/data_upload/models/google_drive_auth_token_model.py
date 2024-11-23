
from datetime import datetime

from pydantic import BaseModel

    
class GoogleDriveAuthToken(BaseModel):
    token: str
    refresh_token: str
    token_uri: str
    universe_domain: str
    expiry:  str