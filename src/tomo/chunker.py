def split_text_into_chunks(text, words_per_chunk=200, overlap_words=40):
    if words_per_chunk <= 0:
        raise ValueError("words_per_chunk must be greater than zero")
    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative")
    if overlap_words >= words_per_chunk:
        raise ValueError("overlap_words must be smaller than words_per_chunk")

    words = text.split()
    if len(words) == 0:
        return []

    step_size = words_per_chunk - overlap_words
    chunks = []
    start_index = 0
    while start_index < len(words):
        end_index = start_index + words_per_chunk
        chunk_words = words[start_index:end_index]
        chunks.append(" ".join(chunk_words))
        if end_index >= len(words):
            break
        start_index = start_index + step_size

    return chunks
