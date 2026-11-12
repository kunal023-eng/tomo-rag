from tomo.embeddings import (
    build_document_embedding_input,
    build_query_embedding_input,
    embed_document_chunk,
    embed_search_query,
)


def test_build_document_embedding_input_adds_document_prefix():
    result = build_document_embedding_input("some chunk text")
    assert result == "search_document: some chunk text"


def test_build_query_embedding_input_adds_query_prefix():
    result = build_query_embedding_input("some user question")
    assert result == "search_query: some user question"


def test_embed_document_chunk_rejects_empty_text():
    try:
        embed_document_chunk("   ")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for empty document chunk")


def test_embed_search_query_rejects_empty_text():
    try:
        embed_search_query("")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for empty search query")
