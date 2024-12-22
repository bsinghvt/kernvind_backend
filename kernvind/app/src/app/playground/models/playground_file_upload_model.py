from pydantic import BaseModel
from quart_schema.pydantic import File
class PlayGroundFileUploadModel(BaseModel):
    file: File
    
class PlayGroundFileUploadResponse(BaseModel):
    token: str