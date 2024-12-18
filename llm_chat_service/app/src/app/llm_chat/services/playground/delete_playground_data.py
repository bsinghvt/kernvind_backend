import logging
from data_models.vector_model import langchain_pg_collection

async def playground_data_delete(datasource_name: str):
    try:
        await langchain_pg_collection.filter(name=datasource_name).delete()
    except Exception as e:
        logging.error(e.__str__())