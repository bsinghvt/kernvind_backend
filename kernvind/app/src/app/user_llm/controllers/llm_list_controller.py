from typing import Any, List
from quart import Blueprint
from quart_schema import  validate_response
from quart import Blueprint



from ..services.llm_list_service import get_available_model_list_service

from ...core.models.error_model import Failure


from ..models.user_llm_model import  LlmListOut


public_llm_bp = Blueprint('public_llm', __name__)

@public_llm_bp.get('/list')
@validate_response(List[LlmListOut], 200)
@validate_response(Failure, 500)
async def public_llm_list_route() -> Any:
    return await get_available_model_list_service()