from datetime import datetime

from pydantic import BaseModel

    
class GoogleDriveFileMetaData(BaseModel):
    file_id: str
    name: str
    size: str
    mime_type: str
    web_view_link: str
    modified_time: datetime