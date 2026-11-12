# TOMO-RAG

A local Retrieval-Augmented Generation (RAG) chatbot that answers questions
about documents stored on the same machine. No cloud services, no API keys,
and no network calls to any external LLM provider. All inference runs through
Ollama.

## How it works

Documents in a folder are read, split into overlapping chunks of words,
converted into numerical vectors with an embedding model, and kept in memory.
When a question is asked, the question is converted into a vector with the
same embedding model, compared against every stored chunk using cosine
similarity, and the most similar chunks are passed to a local language model
as context. The model is told to answer only from those chunks.

## Requirements

- Ubuntu or another Linux distribution
- Python 3.14
- uv package manager
- Ollama with the llama3.2 and nomic-embed-text models

A GPU is optional. Everything runs on CPU as well, though generation is
slower without a GPU.

## Step 1 - Install Ollama and the two models

Install Ollama using the official script:

    curl -fsSL https://ollama.com/install.sh | sh

Check that the service is running:

    sudo systemctl status ollama

Pull the two models this project uses:

    ollama pull llama3.2
    ollama pull nomic-embed-text

Confirm both are present:

    ollama list

## Step 2 - Install the project

If uv is not installed:

    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env

Then, from the project root:

    uv sync

This creates a virtual environment and installs the exact dependency versions
listed in uv.lock. No other install command is needed.

## Step 3 - Add documents

Place files in the documents/ folder:

    cp /path/to/your/file.pdf documents/

Supported file types: pdf, txt, md, docx, pptx, xlsx.

A few notes on how each format is read:

- PDF: text is extracted page by page using pypdf. Scanned PDFs with no text
  layer are skipped with a warning. Tables inside a PDF are flattened into a
  text stream, so row and column structure is lost.
- TXT and MD: read as plain text. Markdown syntax such as #, *, and backticks
  is preserved as characters.
- DOCX: paragraphs are extracted. Text inside tables is not extracted.
- PPTX: text from each slide is extracted along with speaker notes, and each
  slide is prefixed with its slide number.
- XLSX: each row is converted into a labelled line where every cell value is
  prefixed with its column header, and every row is prefixed with its sheet
  name. This keeps cells attached to their meaning after chunking.

## Step 4 - Ask questions

    uv run python scripts/chat.py

To use a different folder:

    uv run python scripts/chat.py /path/to/another/folder

The first run reads and indexes every document in the folder. On a machine
with a GPU, this takes a few seconds per document; on CPU it is slower. Once
indexing finishes, the prompt appears:

    question>

Type a question and press Enter. Type /quit to exit.

## Step 5 - Run the tests

    uv run pytest -v

The unit tests cover the loaders for every supported format, the text
chunker, the embedding prefix handling, the cosine similarity maths, the
top-k retrieval ordering, and the prompt formatter. They do not call Ollama
and run offline in under a second.

## How the code is organised

The pipeline has five stages, each in its own file:

| File | Responsibility |
|---|---|
| src/tomo/loader.py | Reads a document of any supported format into a single string |
| src/tomo/chunker.py | Splits that string into overlapping word windows |
| src/tomo/embeddings.py | Converts each chunk and each question into a 768-dimensional vector using nomic-embed-text |
| src/tomo/search.py | Computes cosine similarity between the question vector and every chunk vector, then returns the top-k chunks |
| src/tomo/generator.py | Builds a prompt with the retrieved excerpts and asks llama3.2 to answer from them |

scripts/chat.py wires the five stages together into the interactive loop.

## Project structure

    tomo-rag/
    |-- README.md
    |-- pyproject.toml
    |-- uv.lock
    |-- documents/            (your documents go here)
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

## Design notes

Two choices affect how well the answers match the source documents:

- nomic-embed-text was trained with two task prefixes, search_document: for
  stored chunks and search_query: for the user question. The code applies the
  correct prefix automatically, so the same model handles both indexing and
  querying without losing accuracy.

- The system instruction for llama3.2 tells the model to answer only from the
  retrieved excerpts, and to say clearly when the answer is not present. This
  reduces invented answers, which matters when the chatbot is used on real
  application or reference material.

## Tuning

Two values in the code affect retrieval quality and can be adjusted without
touching anything else:

- NUMBER_OF_TOP_CHUNKS in scripts/chat.py controls how many chunks are given
  to the model. Raising it gives the model more context; lowering it keeps
  the prompt shorter and faster.

- words_per_chunk and overlap_words in src/tomo/chunker.py control how text
  is split. Smaller chunks give the model more focused excerpts; larger
  chunks preserve more surrounding context per excerpt.

Both interact with the model's context window. If NUMBER_OF_TOP_CHUNKS
multiplied by words_per_chunk grows past the model's context size, older
excerpts are silently dropped by llama3.2.

## Known limitations

The pipeline is a plain dense-retrieval system running a small language model.
In practice it answers many factual questions well, but a few patterns are
harder than others. These are inherent to this kind of setup rather than
bugs:

- Facts mentioned only in passing. When the answer is one sentence inside a
  longer paragraph on a nearby topic, the embedding of the whole chunk may
  not rank above the top-k cutoff, and the model refuses even though the
  sentence is in the corpus. Smaller chunks help; hybrid retrieval (BM25 plus
  cosine) would help more, but it is not implemented here.

- Numeric precision. Small models sometimes round numbers from the source
  (for example, a spreadsheet value of 3.92 can be reported back as 3.9).
  The retrieval is correct; the rounding is a generation artefact.

- Multi-document synthesis. Summarisation questions that pull from several
  documents at once can occasionally mix facts from adjacent periods or
  sections. This is a common limitation of small language models doing
  multi-hop reasoning.

- PDF tables. Tables inside a PDF are extracted as a stream of cell values
  with the row and column structure lost. Single-fact lookups still work,
  but questions that require comparing rows may not. Storing the same data
  in an xlsx file avoids the problem, because the xlsx loader keeps header
  labels attached to each value.

- Self-referential questions. If a document names the generation model itself
  (for example llama3.2), the model may refuse to answer questions about its
  own name. This is a quirk of small models and is not a retrieval issue.

- Scanned PDFs. PDFs that contain images of text rather than a text layer
  produce no extractable text and are skipped with a warning. OCR is not
  part of this project.

These limitations are listed so that behaviour can be judged against them
rather than against a promise of perfect recall.

## Notes on hardware

llama3.2 at the default 4096-token context uses roughly 2 to 3 GiB of VRAM.
On a GPU with less VRAM than that, Ollama falls back to CPU automatically and
generation is slower, but no code change is required.

The chatbot keeps the entire chunk index in memory and rebuilds it on each
start. For a handful of documents this takes a few seconds. This is a
deliberate design choice: it keeps the project small and removes the need for
a database.
