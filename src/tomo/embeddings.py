import ollama

EMBEDDING_MODEL_NAME = "nomic-embed-text"
DOCUMENT_TASK_PREFIX = "search_document: "
QUERY_TASK_PREFIX = "search_query: "


def embed_document_chunk(chunk_text):
    if not chunk_text.strip():
        raise ValueError("Cannot embed an empty document chunk")
    embedding_input = build_document_embedding_input(chunk_text)
    return request_embedding_from_ollama(embedding_input)


def embed_search_query(query_text):
    if not query_text.strip():
        raise ValueError("Cannot embed an empty search query")
    embedding_input = build_query_embedding_input(query_text)
    return request_embedding_from_ollama(embedding_input)


def build_document_embedding_input(chunk_text):
    return DOCUMENT_TASK_PREFIX + chunk_text


def build_query_embedding_input(query_text):
    return QUERY_TASK_PREFIX + query_text


def request_embedding_from_ollama(embedding_input):
    embedding_response = ollama.embed(
        model=EMBEDDING_MODEL_NAME,
        input=embedding_input,
    )
    embedding_vector = embedding_response["embeddings"][0]
    return embedding_vector
