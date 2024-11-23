from typing import List
from ....config import Config
from sqlalchemy.ext.asyncio import AsyncEngine
from langchain_postgres import PGVector
from langchain_core.documents import Document

async def upload_vector_doc_pg(config: Config,
                                engine: AsyncEngine, 
                                datasource_name: str, 
                                docs: List[Document],
                            ):
    embeddings = config.EMBEDDINGS
    vector_store =  PGVector(
        embeddings=embeddings,
        embedding_length=config.EMBEDDINGS_LENGTH,
        collection_name=datasource_name,
        connection=engine,
        use_jsonb=True,
        async_mode=True,
        logger=config.PGVECTOR_LOGGER
    )
    try:
        await vector_store.aadd_documents(documents=docs)
    except Exception as e:
        raise e