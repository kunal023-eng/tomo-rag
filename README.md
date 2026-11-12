# TOMO-RAG

A local Retrieval-Augmented Generation (RAG) chatbot that answers questions
about local PDF and text documents. It runs entirely on the local machine —
no cloud services, no API keys, no network calls to any LLM provider.

Given a folder of documents, the chatbot reads them, splits them into chunks,
converts each chunk into a numerical vector, and stores the vectors in memory.
When a question is asked, the question is converted into a vector using the
same model, compared against every stored vector using cosine similarity, and
the most similar chunks are passed to a local language model as context. The
model is instructed to answer only from those excerpts.

## Requirements

- Ubuntu (or another Linux distribution)
- Python 3.14
- `uv` package manager
- Ollama with the `llama3.2` and `nomic-embed-text` models

A GPU is optional. The instructions below were tested on an NVIDIA GTX 1650
with 3.6 GiB of VRAM. Without a GPU, the same steps work, but generation will
be slower (roughly 10-20x slower for `llama3.2`).

## Step 1 — Install Ollama and the models

Install Ollama using the official script:

    curl -fsSL https://ollama.com/install.sh | sh

Confirm the service is running:

    sudo systemctl status ollama

Pull the two models this project uses:

    ollama pull llama3.2
    ollama pull nomic-embed-text

Verify both are present:

    ollama list

You should see `llama3.2:latest` (about 2.0 GB) and `nomic-embed-text:latest`
(about 274 MB).

## Step 2 — Install the project

If `uv` is not installed:

    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env

Then, from the project root:

    uv sync

This creates a `.venv/` and installs the exact dependency versions listed in
`uv.lock`. It is the only install command needed.

## Step 3 — Add documents

Place your PDF or `.txt` files in the `documents/` folder:

    cp /path/to/your/file.pdf documents/
    cp /path/to/your/notes.txt documents/

Supported file types: `.pdf` and `.txt`. Both are read locally; nothing is
uploaded anywhere.

## Step 4 — Ask questions

    uv run python scripts/chat.py

The first run loads each document, splits it into chunks, and embeds each
chunk. On a GTX 1650 this takes a few seconds per document. After that, the
prompt appears:

    question>

Type a question and press Enter. Type `/quit` to exit.

To use a different documents folder:

    uv run python scripts/chat.py /path/to/another/folder

## Step 5 — Run the unit tests

    uv run pytest -v

28 tests cover the PDF/text loader, the chunker, the embedding prefix logic,
the cosine-similarity math, the top-k retrieval ordering, and the prompt
formatter. The tests do not call Ollama; they run offline in under a second.

## How it works

The pipeline has five stages, each in its own file:

| File | Responsibility |
|---|---|
| `src/tomo/loader.py` | Reads a PDF or text file into a single string |
| `src/tomo/chunker.py` | Splits that string into overlapping word windows |
| `src/tomo/embeddings.py` | Converts each chunk (and each question) into a 768-dimensional vector using `nomic-embed-text` |
| `src/tomo/search.py` | Computes cosine similarity between the question vector and every chunk vector, then returns the top-k chunks |
| `src/tomo/generator.py` | Builds a prompt with the retrieved excerpts and asks `llama3.2` to answer from them |

`scripts/chat.py` wires the five together into the interactive loop.

Two design choices that matter for answer quality:

- `nomic-embed-text` was trained with two task prefixes — `search_document:`
  for stored chunks and `search_query:` for the user's question. The code
  applies the correct prefix automatically, so the same model is used for
  both index and query without sacrificing retrieval accuracy.
- The system instruction tells `llama3.2` to answer only from the retrieved
  excerpts, and to say so when the answer is not present. This reduces
  hallucination, which matters when the chatbot is used on application
  documents.

## Project structure

    tomo-rag/
    |-- README.md
    |-- pyproject.toml
    |-- uv.lock
    |-- documents/            (your PDFs and text files go here)
    |-- scripts/
    |   `-- chat.py           (interactive loop)
    |-- src/tomo/
    |   |-- loader.py
    |   |-- chunker.py
    |   |-- embeddings.py
    |   |-- search.py
    |   `-- generator.py
    `-- tests/
        |-- test_loader.py
        |-- test_chunker.py
        |-- test_embeddings.py
        |-- test_search.py
        `-- test_generator.py

## Notes

- Model size vs. VRAM: `llama3.2` at 4096-token context uses about 2.5 GiB
  of VRAM. If your GPU has less than that, the model will fall back to CPU
  and generation will be slower. No code change is needed.
- The chatbot keeps the chunk index in memory. It is rebuilt on every start,
  which takes a few seconds for a handful of documents. This is deliberate —
  it keeps the project small and removes the need for a database.
