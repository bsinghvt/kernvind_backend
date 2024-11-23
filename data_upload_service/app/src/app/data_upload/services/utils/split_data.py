
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document
from ...models.document_metadata_model import MetaData

RECURSIVE_TEXT_SPLITTER = RecursiveCharacterTextSplitter(
        separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",],
        chunk_size=1000, chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )

async def split_txt(text: str, metadata: MetaData):
    texts =  RECURSIVE_TEXT_SPLITTER.split_text(text=text)
    docs: List[Document] = []
    for txt in texts:
        docs.append(Document(page_content=txt, metadata=metadata.model_dump(exclude_none=True)))
    return docs