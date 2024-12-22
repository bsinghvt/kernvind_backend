import gc
from io import BytesIO
import logging
import uuid

from ..models.playground_file_upload_model import PlayGroundFileUploadResponse

from .utils.jwt_services_utils import create_access_token_util

from ...core.models.error_model import Failure
from quart import current_app

from ..services.utils.pg_vector_upload import upload_vector_doc_pg
from ..models.document_metadata_model import MetaData
from .utils.unstructure_processing import UnstructureProcess
from quart_schema.pydantic import File

async def playgound_file_upload(file: File):
    try:
        st = file.stream
        if not isinstance(st, BytesIO):
            byte_content = st.read()
            st = BytesIO(byte_content)
        mime_type = file.content_type
        if not mime_type:
            return
        unstructured_process = UnstructureProcess(fh=st, 
                                                    mime_type=mime_type, 
                                                    meta_data=MetaData(source_id=file.filename,source_title=file.filename,datafeed_id=0,datafeedsource_id='Playground',datasource_id=0),
                                                    pdf_strategy_fast=True)
        file_data = await unstructured_process.partition()
        st.close()
        if mime_type == 'application/pdf':
            if len(file_data) > 0:
                doc = file_data[len(file_data) - 1]
                page_num = doc.metadata.get('page_number')
                if page_num != None:
                    if int(page_num)  > 100:
                        return Failure(error="Maximum 100-page PDFs are allowed. Please upload a smaller file."), 400
        id = str(uuid.uuid4())
        datasource_name='Playground_' + id
        config = current_app.config['CONFIG'] 

        await upload_vector_doc_pg(engine=current_app.config['PG_ASYNC_ENGINE'],
                                    datasource_name=datasource_name,
                                    config=config,
                                    docs=file_data)

        token = create_access_token_util(identity=datasource_name)
        #del em
        #gc.collect()
        return PlayGroundFileUploadResponse(token=token), 201
    except Exception as e:
        logging.critical(e.__str__())
        return Failure(error="Something went wrong, please try again"), 500