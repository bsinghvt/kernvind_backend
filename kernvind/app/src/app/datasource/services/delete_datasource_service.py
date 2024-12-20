import logging

from data_models.vector_model import langchain_pg_collection
from ...core.models.success_model import Success
from data_models.bot_model import DataSource
from tortoise.transactions import  in_transaction

from ...core.models.error_model import Failure


async def delete_datasource(user_id:int, datasource_id: int):
    try:
        async with in_transaction() as connection:
            datasource =  await DataSource.filter(created_by_user_id=user_id, datasource_id=datasource_id)
            if len(datasource) == 0:
                return Failure(error="User is Unauthorized to delete datasource"), 401
            datasource_name = datasource[0].datasource_name
            
            await DataSource.filter(created_by_user_id=user_id, datasource_id=datasource_id).delete() 
            await langchain_pg_collection.filter(name=datasource_name).delete()
        return Success(msg='Datasource is deleted')
        
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500