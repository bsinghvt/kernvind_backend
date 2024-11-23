import logging
from typing import List
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import AsyncEngine
from youtube_transcript_api import YouTubeTranscriptApi
from ....config import Config
from ..utils.pg_vector_upload import upload_vector_doc_pg
from ...models.document_metadata_model import MetaData
from unstructured.cleaners.core import clean_non_ascii_chars

YOUTUBE_URL = 'https://www.youtube.com/watch?v='

async def extract_youtube_transcript(datafeed_source_unique_id: str,
                                    datafeed_source_title: str,
                                    datafeedsource_id: str,
                                    datasource_name: str,
                                    datafeed_id: int,
                                    datasource_id: int,
                                    engine: AsyncEngine, 
                                    config: Config,
                                    ):
    docs: List[Document] = []
    try:
        cc_list = []
        chunk_len = 0
        transcript_list = YouTubeTranscriptApi.get_transcript(datafeed_source_unique_id, languages=['en', 'en-GB'])
        cc: str
        time_int: int | None 
        start_time = []
        for transcript in transcript_list:
            time_int = None
            try:
                time_float = float(transcript['start'])
                time_int = int(time_float)
            except Exception as e:
                logging.error(f'Failed to parse: {transcript['start']}')
            cc = transcript['text']
            cc = clean_non_ascii_chars(cc).replace('\n' , ' ')
            if not time_int:
                time_int = 0
            docs.append(Document(page_content=cc + '\n', metadata=MetaData(source_id=f'{YOUTUBE_URL}{datafeed_source_unique_id}&t={time_int}s',
                                        datafeedsource_id=datafeedsource_id, 
                                        source_title=datafeed_source_title,
                                        datasource_id=datasource_id,
                                        datafeed_id=datafeed_id).model_dump(exclude_none=True)))
            """
            if time_int:
                if len(start_time) == 0:
                    start_time.append(time_int)
                cc = f'Caption start time: {time_int} | Caption: {transcript['text']}'
            else:
                cc = f'Caption: {transcript['text']}'
            
            cc = clean_non_ascii_chars(cc).replace('\n' , ' ')
            chunk_len = chunk_len + len(cc)
            cc_list.append(cc)
            if chunk_len > 1000:
                if len(start_time) == 0:
                    start_time.append(0)
                page_content = 'These are video captions and caption start time: \n' + '\n'.join(cc_list)
                docs.append(Document(page_content=page_content, metadata=MetaData(source_id=f'{YOUTUBE_URL}{datafeed_source_unique_id}?t={start_time[0]}s',
                                        datafeedsource_id=datafeedsource_id, 
                                        source_title=datafeed_source_title,
                                        datasource_id=datasource_id,
                                        datafeed_id=datafeed_id).model_dump(exclude_none=True)))
                cc_list = []
                chunk_len = 0
            """
        if len(cc_list) > 0:
            if len(start_time) == 0:
                start_time.append(0)
            page_content = 'These are video captions and caption start time: \n' + '\n'.join(cc_list)
            docs.append(Document(page_content=page_content, metadata=MetaData(source_id=f'{YOUTUBE_URL}{datafeed_source_unique_id}?t={start_time[0]}s',
                                                                            source_title=datafeed_source_title,
                                                                            datafeedsource_id=datafeedsource_id, 
                                                                            datasource_id=datasource_id,
                                                                            datafeed_id=datafeed_id).model_dump(exclude_none=True)))
        await upload_vector_doc_pg(engine=engine,
                                datasource_name=datasource_name,
                                config=config,
                                docs=docs)
    except Exception as e:
        resp = Exception(f'Error while loading youtube link: {datafeed_source_unique_id}. {e.__str__()}')
        raise resp
    
