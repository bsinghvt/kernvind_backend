from collections import defaultdict, deque
import logging
from operator import itemgetter
from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_postgres import PGVector
#from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from quart import current_app


template = """Answer the question based on your knowledge.  
The current question may or may not reference context from the chat history (if available).  

Chat History:  
{history}  

Current Question:  
{question}
"""

YTT_PROMPT = """You are an AI assistant specializing in extracting and synthesizing information from XML-formatted data provided within <context></context> tags.

Each <source> element contains <link>, <title>, and <content>. The <source> element may also include optional <page_name> and <page_number> elements.

<context>
{context}
</context>

When answering:  
- If the provided context lacks enough information to answer, respond: "I'm sorry, but I don't have enough information to answer this question.
- If the information is ambiguous or unclear, ask for clarification from the user.  
- Provide sources using numbered citations ([1], [2], etc.) and list them at the end of the response in IEEE format. Each citation should include the <title>, <link>, <page_name>, and <page_number> where available. Exclude optional elements if they are not present. Do not use XML tags; include only the values.

Question:  
{question}  

Answer:""
"""
contextualize_q_system_prompt = """
Given a chat history and the latest user question, which may or may not reference context from the chat history, reformulate the question into a standalone version that can be understood without relying on the prior conversation. Output only the question, with no additional details.  
Do not provide an answer to the question.  
If no reformulation is required, return the question as is, without adding any extra information.  

Chat History:  
{history}  

Current Question:  
{question}
"""
prompt = ChatPromptTemplate.from_template(template)


async def get_history(msgs: deque[tuple[str, str]]):
    if len(msgs) == 0:
        return ''
    history = []
    for msg in msgs:
        history.append('Question: ' + msg[0] + '\nAnswer: ' + msg[1])
    return '\n\n'.join(history)

def format_docs(docs: List[Document]):
    return "\n".join(doc.page_content for doc in docs)

def format_docs_xml(docs: List[Document]) -> str:
    formatted = []
    sources = defaultdict(list)
    for i, doc in enumerate(docs):
        key: tuple[str, str, str, str] = (doc.metadata['source_id'], doc.metadata.get('source_title',''), doc.metadata.get('page_number',''), doc.metadata.get('page_name',''))
        sources[key].append(doc.page_content)
    page_name = ''
    page_number = ''
    source_id = ''
    source_title = ''
    doc_str = ''
    page_node = ''
    page_number_node = ''
    for k, v in sources.items():
        page_node = ''
        page_number_node = ''
        source_id, source_title, page_number, page_name = k
        content = '\n'.join(v)
        if page_name:
            page_node = f'<page_name>{page_name}</page_name>'
        if page_number:
            page_number_node = f'<page_number>{page_number}</page_number>'
        doc_str = f"""\
        <source link=\"{source_id}\">
            <title>{source_title}</title>
            {page_node}
            {page_number_node}
            <content>{content}</content>
        </source>"""
        formatted.append(doc_str)
    return "\n\n<sources>" + "\n".join(formatted) + "</sources>"

async def runllm_playground_with_rag(question: str, datasource_name: str, chat_history: deque[tuple[str, str]], llm: BaseChatModel | None = None):
    if not llm:
        yield 'Some error occured,'
        logging.critical('LLM instance is None')
        return
    
    if not datasource_name:
        yield 'Some error occured,'
        logging.critical('playground datasource_name is None')
        return
    vector_store =  PGVector(
                embeddings=current_app.config['EMBEDDINGS'],
                embedding_length=current_app.config['EMBEDDINGS_LENGTH'],
                collection_name=datasource_name,
                connection=current_app.config['PG_ASYNC_ENGINE'],
                use_jsonb=True,
                async_mode=True,
            )
    try:
        history = await get_history(chat_history)
        setup_and_retrieval = None
        retriever: Optional[VectorStoreRetriever] = None
        if vector_store:
            retriever = vector_store.as_retriever(search_type='mmr', search_kwargs={"k": 10, 'fetch_k': 25})
            #setup_and_retrieval = RunnableParallel({"context": retriever | format_docs_xml, "question": RunnablePassthrough()})
            setup_and_retrieval = {
                "context": itemgetter("question") | retriever | format_docs_xml,
                "question": itemgetter("question"),
                "history": itemgetter("history"),
                }
        if setup_and_retrieval:
            if history:
                history_prompt  = ChatPromptTemplate.from_template(contextualize_q_system_prompt)
                history_chain = history_prompt | llm | StrOutputParser()
                new_question = await history_chain.ainvoke({'question' : question, 'history': history})
                print(new_question)
                question = new_question
            rag_prompt  = ChatPromptTemplate.from_template(YTT_PROMPT)
            chain = setup_and_retrieval | rag_prompt | llm | StrOutputParser()
            async for chunk in chain.astream({'question' : question, 'history': history}):
                yield chunk
        else:
            chain = prompt | llm | StrOutputParser()
            async for chunk in chain.astream({'question' : question, 'history': history}):
                yield chunk
    except Exception as e:
        yield 'Some error occured,'
        logging.critical(e.__str__())