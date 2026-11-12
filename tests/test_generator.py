from tomo.generator import (
    build_user_message,
    format_chunks_as_context,
    generate_answer,
)


def test_format_chunks_labels_each_excerpt():
    top_chunks = [(0.9, "first chunk text"), (0.7, "second chunk text")]
    context_block = format_chunks_as_context(top_chunks)
    assert "[Excerpt 1]" in context_block
    assert "first chunk text" in context_block
    assert "[Excerpt 2]" in context_block
    assert "second chunk text" in context_block


def test_format_chunks_preserves_order():
    top_chunks = [(0.9, "highest score"), (0.3, "lowest score")]
    context_block = format_chunks_as_context(top_chunks)
    assert context_block.index("highest score") < context_block.index("lowest score")


def test_build_user_message_contains_context_and_question():
    user_message = build_user_message("some context", "what is the deadline?")
    assert "some context" in user_message
    assert "what is the deadline?" in user_message


def test_generate_answer_rejects_empty_question():
    try:
        generate_answer("   ", [(0.9, "some chunk")])
    except ValueError:
        return
    raise AssertionError("Expected ValueError for empty question")


def test_generate_answer_rejects_empty_chunks():
    try:
        generate_answer("a real question", [])
    except ValueError:
        return
    raise AssertionError("Expected ValueError for empty chunk list")
