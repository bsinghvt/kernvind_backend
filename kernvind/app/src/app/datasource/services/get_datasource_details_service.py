import logging
from typing import List, cast
from data_models.bot_model import DataSource

from data_models.datasource_model import DataFeed
from data_models.user_model import User
from tortoise.query_utils import Prefetch


from ..models.datasource_details_model import DatasourceDetails

from ..models.new_datasource_models import DataSourceFeed
from ..models.get_datasource_list_model import DataSourceList
from ...core.models.error_model import Failure


async def datasource_details(user_id:int, datasource_id: int):
    try:
        datasources =  await DataSource.filter(created_by_user_id=user_id, datasource_id=datasource_id)
        if len(datasources) == 0:
            return Failure(error="User is Unauthorized to get datasource"), 401
        if len(datasources) > 1:
            return Failure(error="Something went wrong, please try again"), 500
        datasource = datasources[0]

        datasource_out = DataSourceList(datasource_name=datasource.datasource_name,
                    datasource_description=datasource.datasource_description,
                    datasource_id=datasource.datasource_id,
                    created=datasource.created,
                    modified=datasource.modified,
                    created_by_user_id=datasource.created_by_user_id) # type: ignore
        
        datafeeds_list: List[DataSourceFeed] = []
        user_prefetch = Prefetch('created_by_user', queryset=User.all().only('full_name', 'user_id','email'))
        datafeeds = DataFeed.filter(datasource_id=datasource_id).only('datafeed_id',
                                                        'datafeed_name',
                                                        'datafeed_source_unique_id',
                                                        'datafeed_source_title',
                                                        'datafeed_description',
                                                        'created_by_user_id',
                                                        'datafeedsource_id',
                                                        'datafeedloadstatus_id',
                                                        'created',
                                                        'modified').prefetch_related(user_prefetch)
        async for datafeed in datafeeds:
            user =  cast(User, datafeed.created_by_user)
            datafeedsource_id: str = datafeed.datafeedsource_id # type: ignore
            datafeedloadstatus_id: str = datafeed.datafeedloadstatus_id # type: ignore
            datafeeds_list.append(DataSourceFeed(datafeed_id=datafeed.datafeed_id,
                        datafeed_name=datafeed.datafeed_name,
                        datafeed_description=datafeed.datafeed_description,
                        datafeedsource_id=datafeedsource_id,
                        created_by_user_id=user.user_id,
                        created_by_name=user.full_name,
                        datafeed_source_unique_id=datafeed.datafeed_source_unique_id,
                        datafeed_source_title=datafeed.datafeed_source_title,
                        datafeedloadstatus_id=datafeedloadstatus_id,
                        created=datafeed.created,
                        modified=datafeed.modified))
        return DatasourceDetails(datasource=datasource_out, datafeeds=datafeeds_list), 200
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500