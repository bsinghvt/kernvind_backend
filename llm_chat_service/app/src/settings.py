from sentence_transformers import SentenceTransformer

MILVUS_HOST = 'milvus-standalone'
MILVUS_PORT = 19530
MILVUS_EMBEDDING_VECTOR_DIMENSION = 384
MILVUS_HTTP_PROTOCOL = 'http'

MILVUS_CONNECTION_STRING = f'{MILVUS_HTTP_PROTOCOL}://{MILVUS_HOST}:{MILVUS_PORT}'


MODEL_NAME = "all-MiniLM-L6-v2"
DEVICE = 'cpu'
EMBEDDINGS = SentenceTransformer(model_name_or_path=MODEL_NAME,  device=DEVICE)