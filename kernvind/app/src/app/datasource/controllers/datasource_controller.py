
import logging
from typing import Any, List

from ..services.delete_datafeed_service import delete_datafeed

from ..models.datasource_datafeed_add_model import DataSourceAddFeed

from ..services.add_datafeed_service import add_datasource_feed

from ..services.delete_datasource_service import delete_datasource
from ...core.models.success_model import Success
from quart import Blueprint
from quart_schema import  validate_headers, validate_request, validate_response
from quart import Blueprint

from ..models.datasource_update_model import DataSourceUpdate

from ..models.datasource_details_model import DatasourceDetails
from ..services.get_datasource_details_service import datasource_details

from ...core.models.user_claims_model import UserClaims
from ...core.models.headers_model import Headers
from ...core.models.error_model import Failure

from ..models.get_datasource_list_model import DataSourceList
from ..services.update_datasource_service import update_datasource
from ..services.get_datasource_list_service import datasource_list
from ..services.create_datasource_service import create_datasource
from ..models.new_datasource_models import  DataSourceIn, DataSourceOut


from quart_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims,
)


datasource_bp = Blueprint('datasource', __name__)

@datasource_bp.delete('/deletefeed/<datafeed_id>')
@validate_response(DatasourceDetails, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 409)
@validate_response(Failure, 400)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def datasource_delete_feed(datafeed_id: str, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    datafeed_id_int: int
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    try:
        datafeed_id_int = int(datafeed_id)
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="Not a valid datafeed"), 400
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    resp = await delete_datafeed(user_id=current_user,datafeed_id=datafeed_id_int)
    return resp

@datasource_bp.put('/addfeed')
@validate_request(DataSourceAddFeed)
@validate_response(DatasourceDetails, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 409)
@validate_response(Failure, 400)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def datasource_add_feed(data: DataSourceAddFeed, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    resp = await add_datasource_feed(user_id=current_user,datasourceAddFeed=data)
    return resp

@datasource_bp.put('/updatedesc')
@validate_request(DataSourceUpdate)
@validate_response(DatasourceDetails, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def datasource_update(data: DataSourceUpdate, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    datasource_id = data.datasource_id
    description = data.datasource_description
    resp = await update_datasource(user_id=current_user,datasource_id=datasource_id, datasource_description=description)
    return resp


@datasource_bp.delete('/<datasource_id>')
@validate_response(Success, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def datasource_delete(headers: Headers, datasource_id: str) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    datasource_id_int: int
    try:
        datasource_id_int = int(datasource_id)
    except Exception as e:
        return Failure(error='Not a valid request') , 400
    resp = await delete_datasource(user_id=current_user,datasource_id=datasource_id_int)
    return resp

@datasource_bp.get('/<datasource_id>')
@validate_response(DatasourceDetails, 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def details_datasources(headers: Headers, datasource_id: str) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401
    datasource_id_int: int
    try:
        datasource_id_int = int(datasource_id)
    except Exception as e:
        return Failure(error='Not a valid request') , 400
    resp = await datasource_details(user_id=current_user,datasource_id=datasource_id_int)
    return resp


@datasource_bp.get('/list')
@validate_response(List[DataSourceList], 200)
@validate_response(Failure, 500)
@validate_response(Failure, 401)
@jwt_required
@validate_headers(Headers)
async def list_datasources(headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if not full_name or not current_user:
        return Failure(error="current user unauthenticated"), 401

    resp = await datasource_list(current_user)
    return resp

@datasource_bp.post('/create')
@jwt_required
@validate_headers(Headers)
@validate_request(DataSourceIn)
@validate_response(DataSourceOut, 201)
@validate_response(Failure, 409)
@validate_response(Failure, 400)
@validate_response(Failure, 401)
@validate_response(Failure, 500)
async def datasource_create(data: DataSourceIn, headers: Headers) -> Any:
    current_user: int = get_jwt_identity()
    user_claims = get_jwt_claims()
    full_name = ''
    try:
        user_claims_obj = UserClaims.model_validate(user_claims)
        full_name = user_claims_obj.full_name
    except Exception as e:
        logging.error(e.__str__())
        return Failure(error="current user name unauthenticated"), 401
    
    if full_name != data.created_by_name:
        return Failure(error="unauthenticated"), 401
    if data.created_by_user_id != current_user:
        return Failure(error="unauthenticated"), 401

    resp = await create_datasource(datasource_in=data)
    return resp