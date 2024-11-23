import logging
from data_models.bot_model import DataSource


from .get_datasource_details_service import datasource_details

from ...core.models.error_model import Failure


async def update_datasource(user_id:int, datasource_id: int, datasource_description: str):
    try:
        datasource =  await DataSource.filter(created_by_user_id=user_id, datasource_id=datasource_id).update(datasource_description=datasource_description)
        if not datasource:
            return Failure(error="User is Unauthorized to update datasource"), 401
        
        return await datasource_details(user_id, datasource_id)
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500