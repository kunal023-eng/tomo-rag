from tomo.chunker import split_text_into_chunks


def test_short_text_returns_single_chunk():
    chunks = split_text_into_chunks("one two three", words_per_chunk=10, overlap_words=2)
    assert len(chunks) == 1
    assert chunks[0] == "one two three"


def test_empty_text_returns_no_chunks():
    chunks = split_text_into_chunks("", words_per_chunk=10, overlap_words=2)
    assert chunks == []


def test_long_text_is_split_with_overlap():
    text = " ".join(f"word{index}" for index in range(25))
    chunks = split_text_into_chunks(text, words_per_chunk=10, overlap_words=3)
    assert len(chunks) == 4
    last_words_of_first_chunk = chunks[0].split()[-3:]
    first_words_of_second_chunk = chunks[1].split()[:3]
    assert last_words_of_first_chunk == first_words_of_second_chunk


def test_chunks_never_exceed_word_limit():
    text = " ".join(f"word{index}" for index in range(100))
    chunks = split_text_into_chunks(text, words_per_chunk=20, overlap_words=5)
    for chunk in chunks:
        assert len(chunk.split()) <= 20


def test_overlap_not_smaller_than_chunk_raises():
    try:
        split_text_into_chunks("some text", words_per_chunk=10, overlap_words=10)
    except ValueError:
        return
    raise AssertionError("Expected ValueError when overlap_words is not smaller than words_per_chunk")
