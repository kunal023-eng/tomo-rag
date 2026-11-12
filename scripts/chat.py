import sys
from pathlib import Path

from tomo.chunker import split_text_into_chunks
from tomo.embeddings import embed_document_chunk, embed_search_query
from tomo.generator import generate_answer
from tomo.loader import load_document_text
from tomo.search import find_top_k_chunks

DEFAULT_DOCUMENTS_DIRECTORY = Path("documents")
SUPPORTED_FILE_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".pptx", ".xlsx"}
NUMBER_OF_TOP_CHUNKS = 8


def main():
    documents_directory = choose_documents_directory()

    if not documents_directory.exists():
        print(f"Documents directory does not exist: {documents_directory}")
        print("Create it and put your PDF or text files inside, then run again.")
        sys.exit(1)

    document_paths = list_supported_documents(documents_directory)
    if len(document_paths) == 0:
        print(f"No supported documents found in {documents_directory}")
        sys.exit(1)

    print(f"Loading and indexing {len(document_paths)} document(s) from {documents_directory}")
    chunk_texts, chunk_vectors = build_chunk_index(document_paths)

    if len(chunk_texts) == 0:
        print("No text could be indexed from the provided documents.")
        sys.exit(1)

    print(f"Indexed {len(chunk_texts)} chunk(s). Type a question, or /quit to exit.\n")
    run_question_loop(chunk_texts, chunk_vectors)


def choose_documents_directory():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return DEFAULT_DOCUMENTS_DIRECTORY


def list_supported_documents(documents_directory):
    document_paths = []
    for path in sorted(documents_directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_FILE_EXTENSIONS:
            document_paths.append(path)
    return document_paths


def build_chunk_index(document_paths):
    chunk_texts = []
    chunk_vectors = []

    for document_path in document_paths:
        try:
            document_text = load_document_text(document_path)
        except (ValueError, FileNotFoundError) as load_error:
            print(f"  skipped {document_path.name}: {load_error}")
            continue

        document_chunks = split_text_into_chunks(document_text)
        for chunk_text in document_chunks:
            chunk_vector = embed_document_chunk(chunk_text)
            chunk_texts.append(chunk_text)
            chunk_vectors.append(chunk_vector)

        print(f"  indexed {document_path.name} ({len(document_chunks)} chunks)")

    return chunk_texts, chunk_vectors


def run_question_loop(chunk_texts, chunk_vectors):
    while True:
        try:
            raw_question = input("question> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        question = raw_question.strip()
        if question == "":
            continue
        if question == "/quit":
            break

        answer = answer_question(question, chunk_texts, chunk_vectors)
        print(f"\n{answer}\n")


def answer_question(question, chunk_texts, chunk_vectors):
    query_vector = embed_search_query(question)
    top_chunks = find_top_k_chunks(
        query_vector,
        chunk_vectors,
        chunk_texts,
        NUMBER_OF_TOP_CHUNKS,
    )
    return generate_answer(question, top_chunks)


if __name__ == "__main__":
    main()
