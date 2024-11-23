from typing import cast
from quart import current_app
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain_postgres import PGVector

async def get_pgvector_instance(datasource_name: str, datasource_id: int, bot_id: int):
    engine: AsyncEngine = current_app.config['PG_ASYNC_ENGINE']
    embeddings = current_app.config['EMBEDDINGS']
    pg_vector_instance_dict = current_app.config['LC_PG_VECTOR_INSTANCE_COLLECTION']
    if datasource_id not in pg_vector_instance_dict or not pg_vector_instance_dict[datasource_id]:
        vector_store =  PGVector(
                embeddings=embeddings,
                embedding_length=current_app.config['EMBEDDINGS_LENGTH'],
                collection_name=datasource_name,
                connection=engine,
                use_jsonb=True,
                async_mode=True,
            )
        pg_vector_instance_dict[datasource_id] = vector_store
    bot_pg_vector_collection = current_app.config['LC_PG_VECTOR_INSTANCE_COLLECTION_FOR_BOT']
    bot_pg_vector_collection[bot_id] = pg_vector_instance_dict[datasource_id]