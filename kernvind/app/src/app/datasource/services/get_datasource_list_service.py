import logging
from typing import List, Optional, cast
from data_models.bot_model import Bot, DataSource
from tortoise.fields.relational import ReverseRelation

from ..models.get_datasource_list_model import DataSourceList
from ...core.models.error_model import Failure


async def datasource_list(user_id:int):
    try:
        datasources =  DataSource.filter(created_by_user_id=user_id)
        
        datasources_list: List[DataSourceList] = []
        async for datasource in datasources:
            datasources_list.append(DataSourceList(datasource_name=datasource.datasource_name,
                                                datasource_description=datasource.datasource_description,
                                                datasource_id=datasource.datasource_id,
                                                created=datasource.created,
                                                modified=datasource.modified,
                                                created_by_user_id=datasource.created_by_user_id)) # type: ignore
        return datasources_list
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500