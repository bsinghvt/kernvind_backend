import logging

from data_models.vector_model import langchain_pg_embedding

from data_models.datasource_model import DataFeed

from .get_datasource_details_service import datasource_details
from ...core.models.success_model import Success
from tortoise.transactions import  in_transaction

from ...core.models.error_model import Failure


async def delete_datafeed(user_id:int, datafeed_id: int):
    try:
        async with in_transaction() as connection:
            datafeed =  await DataFeed.filter(created_by_user_id=user_id, datafeed_id=datafeed_id)
            if len(datafeed) == 0:
                return Failure(error="User is Unauthorized to delete datafeed"), 401
            datafeed_id = datafeed[0].datafeed_id
            datasource_id = datafeed[0].datasource_id # type: ignore
            await DataFeed.filter(datafeed_id=datafeed_id).delete() 
            datafeed_em = await langchain_pg_embedding.filter(cmetadata__filter={'datafeed_id' : f'{datafeed_id}'}).delete()
            if not datafeed_em:
                return Failure(error="User is Unauthorized to delete datafeed"), 401
        return await datasource_details(user_id, datasource_id)
        
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500