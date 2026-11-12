import ollama

GENERATION_MODEL_NAME = "llama3.2"
CONTEXT_WINDOW_SIZE = 4096
LOW_RANDOMNESS_TEMPERATURE = 0.2

SYSTEM_INSTRUCTION = (
    "You answer questions using only the document excerpts provided by the user. "
    "If the answer is not present in the excerpts, say clearly that the documents "
    "do not contain the answer. Do not invent facts, do not rely on outside knowledge, "
    "and keep the answer concise."
)


def generate_answer(question, top_chunks):
    if not question.strip():
        raise ValueError("Cannot generate an answer for an empty question")
    if len(top_chunks) == 0:
        raise ValueError("Cannot generate an answer without any retrieved chunks")

    context_block = format_chunks_as_context(top_chunks)
    user_message = build_user_message(context_block, question)

    chat_messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_message},
    ]

    chat_response = ollama.chat(
        model=GENERATION_MODEL_NAME,
        messages=chat_messages,
        options={
            "num_ctx": CONTEXT_WINDOW_SIZE,
            "temperature": LOW_RANDOMNESS_TEMPERATURE,
        },
    )
    return chat_response["message"]["content"]


def format_chunks_as_context(top_chunks):
    formatted_excerpts = []
    for excerpt_number, scored_chunk in enumerate(top_chunks, start=1):
        chunk_text = scored_chunk[1]
        formatted_excerpts.append(f"[Excerpt {excerpt_number}]\n{chunk_text}")
    return "\n\n".join(formatted_excerpts)


def build_user_message(context_block, question):
    return f"Document excerpts:\n{context_block}\n\nQuestion: {question}"
