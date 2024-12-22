from typing import Any

from ...core.models.error_model import Failure

from ..services.payground_file_upload_service import playgound_file_upload

from quart_schema import DataSource, validate_request, validate_response
from ..models.playground_file_upload_model import PlayGroundFileUploadModel, PlayGroundFileUploadResponse
from quart import Blueprint

dataupload_bp = Blueprint('dataupload', __name__)

@dataupload_bp.get('/health')
async def health_check()->Any:
    return 'ok'

@dataupload_bp.post('/playground')
@validate_response(PlayGroundFileUploadResponse, 201)
@validate_response(Failure, 500)
@validate_response(Failure, 400)
@validate_request(PlayGroundFileUploadModel, source=DataSource.FORM_MULTIPART)
async def playground_data_upload(data: PlayGroundFileUploadModel)->Any:
    resp = await playgound_file_upload(file=data.file)
    return resp