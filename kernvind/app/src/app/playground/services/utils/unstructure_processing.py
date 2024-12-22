from io import BytesIO
from typing import List
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.docx import partition_docx
from unstructured.partition.doc import partition_doc
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.csv import partition_csv
from unstructured.partition.text import partition_text
from unstructured.documents.elements import Element

from ...models.document_metadata_model import MetaData
from langchain_core.documents import Document
from collections import defaultdict

MS_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
MS_DOC = 'application/msword'
PDF = 'application/pdf'
CSV = 'text/csv'
XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
XLS = 'application/vnd.ms-excel'
TXT = 'text/plain'

class UnstructureProcess:
    _elements: List[Element]
    def __init__(self, fh: BytesIO, mime_type: str, meta_data: MetaData, pdf_strategy_fast=False) -> None:
        self._fh = fh
        self._mime_type = mime_type
        self._meta_data = meta_data
        self._pdf_strategy_fast = pdf_strategy_fast
        
    async def partition(self):
        try:
            if self._mime_type == MS_DOCX:
                return await self._ms_docx()
            elif self._mime_type == MS_DOC:
                return await self._ms_doc()
            elif self._mime_type == PDF and self._pdf_strategy_fast == False:
                return await self._pdf()
            elif self._mime_type == PDF and self._pdf_strategy_fast == True:
                return await self._pdf_fast()
            elif self._mime_type == CSV:
                return await self._csv()
            elif self._mime_type == XLSX:
                return await self._xls_xlsx()
            elif self._mime_type == XLS:
                return await self._xls_xlsx()
            elif self._mime_type == TXT:
                return await self._text()
            else:
                raise Exception(f'{self._mime_type} is not supported')
        except Exception:
            raise
    
    async def _ms_docx(self):
        try:
            self._elements = partition_docx(file=self._fh,chunking_strategy="basic",
                                        infer_table_structure=True,
                                        strategy='hi_res')
            return await self._process_elements_basic_chunk()
        except Exception as e:
            raise
        
    async def _ms_doc(self):
        try:
            self._elements = partition_doc(file=self._fh,chunking_strategy="basic",
                                        infer_table_structure=True,
                                        strategy='hi_res')
            return await self._process_elements_basic_chunk()
        except Exception as e:
            raise
        
    async def _csv(self):
        try:
            self._elements = partition_csv(file=self._fh,
                                        infer_table_structure=True,
                                        strategy='hi_res')
            return await self._process_elements_spreadsheet()
        except Exception as e:
            raise
        
    async def _xls_xlsx(self):
        try:
            self._elements = partition_xlsx(file=self._fh,
                                        infer_table_structure=True,
                                        strategy='hi_res')
            return await self._process_elements_spreadsheet()
        except Exception as e:
            raise

    async def _pdf(self):
        try:
            self._elements = partition_pdf(file=self._fh,
                                        infer_table_structure=True,
                                        strategy='hi_res')
            return await self._process_elements_pdf()
        except Exception as e:
            raise
        
    async def _pdf_fast(self):
        try:
            self._elements = partition_pdf(file=self._fh,
                                        strategy='fast')
            return await self._process_elements_pdf()
        except Exception as e:
            raise
    
    async def _text(self):
        try:
            self._elements = partition_text(file=self._fh,chunking_strategy="basic")
            return await self._process_elements_basic_chunk()
        except Exception as e:
            raise
    
    async def _process_elements_basic_chunk(self):
        meta_data = self._meta_data.model_dump(exclude_none=True)
        docs: List[Document] = []
        for elm in self._elements: 
            if elm.category == 'Table':
                if elm.metadata and elm.metadata.text_as_html:
                    docs.append(Document(page_content=elm.metadata.text_as_html, metadata=meta_data))
                else:
                    docs.append(Document(page_content=elm.text, metadata=meta_data))
            else:
                docs.append(Document(page_content=elm.text, metadata=meta_data))
        return docs
    
    async def _process_elements_spreadsheet(self):
        docs: List[Document] = []
        titles = []
        for elm in self._elements: 
            if elm.metadata.page_name:
                self._meta_data.page_name = elm.metadata.page_name
            meta_data = self._meta_data.model_dump(exclude_none=True)
            if elm.category == 'Title':
                titles.append(elm.text)
            elif elm.category == 'Table':
                current_title = '\n'.join(titles)
                titles = []
                if elm.metadata and elm.metadata.text_as_html:
                    docs.append(Document(page_content=f'{current_title}\n\n{elm.metadata.text_as_html}', metadata=meta_data))
                else:    
                    docs.append(Document(page_content=f'{current_title}\n\n{elm.text}', metadata=meta_data))
            else:
                current_title = '\n'.join(titles)
                titles = []
                docs.append(Document(page_content=f'{current_title}\n\n{elm.text}', metadata=meta_data))
        return docs
    
    async def _process_elements_pdf(self):
        docs: List[Document] = []
        current_title = ''
        title_dict = defaultdict(list)
        title_dict_str = defaultdict(str)
        page_cntr = defaultdict(int)
        current_title = ''
        for elm in self._elements:
            if elm.metadata.page_number:
                page_cntr[elm.metadata.page_number] = 1
            if elm.category == 'Title':
                current_title = elm.text
                if elm.metadata.page_number and current_title:
                    title_dict[elm.metadata.page_number].append(current_title)
        if len(page_cntr) < 15:
            current_titles = []
            for elm in self._elements:
                current_title = '' 
                if elm.metadata.page_number:
                    self._meta_data.page_number = f'{elm.metadata.page_number}'
                meta_data = self._meta_data.model_dump(exclude_none=True)
                if elm.category == 'Title':
                    current_titles.append(elm.text)
                elif elm.category == 'Table': 
                    if len(current_titles) > 0:
                        current_title = '\n'.join(current_titles) + '\n\n'
                        current_titles = []
                    if elm.metadata and elm.metadata.text_as_html:
                        docs.append(Document(page_content=f'{current_title}{elm.metadata.text_as_html}', metadata=meta_data))
                    else:    
                        docs.append(Document(page_content=f'{current_title}{elm.text}', metadata=meta_data))
                else:
                    if len(current_titles) > 0:
                        current_title = '\n'.join(current_titles) + '\n\n'
                        current_titles = []
                    docs.append(Document(page_content=f'{current_title}{elm.text}', metadata=meta_data))
            return docs
        
        for k, v in title_dict.items():
            title_dict_str[k]= '\n'.join(v)
        
        current_title = ''
        for elm in self._elements: 
            if elm.metadata.page_number:
                current_title = title_dict_str.get(elm.metadata.page_number, current_title)
            if elm.metadata.page_number:
                self._meta_data.page_number = f'{elm.metadata.page_number}'
            meta_data = self._meta_data.model_dump(exclude_none=True)
            if elm.category == 'Table':
                if elm.metadata and elm.metadata.text_as_html:
                    docs.append(Document(page_content=f'{current_title}\n\n{elm.metadata.text_as_html}', metadata=meta_data))
                else:    
                    docs.append(Document(page_content=f'{current_title}\n\n{elm.text}', metadata=meta_data))
            else:
                docs.append(Document(page_content=f'{current_title}\n\n{elm.text}', metadata=meta_data))
        return docs