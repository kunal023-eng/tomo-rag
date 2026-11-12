from tomo.search import (
    compute_similarity_scores,
    cosine_similarity,
    find_top_k_chunks,
)


def test_identical_vectors_have_similarity_one():
    score = cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert abs(score - 1.0) < 1e-9


def test_orthogonal_vectors_have_similarity_zero():
    score = cosine_similarity([1.0, 0.0], [0.0, 1.0])
    assert abs(score - 0.0) < 1e-9


def test_opposite_vectors_have_similarity_minus_one():
    score = cosine_similarity([1.0, 2.0], [-1.0, -2.0])
    assert abs(score + 1.0) < 1e-9


def test_mismatched_lengths_raise():
    try:
        cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0])
    except ValueError:
        return
    raise AssertionError("Expected ValueError for mismatched vector lengths")


def test_zero_vector_raises():
    try:
        cosine_similarity([0.0, 0.0], [1.0, 2.0])
    except ValueError:
        return
    raise AssertionError("Expected ValueError for zero vector")


def test_scores_are_computed_for_each_chunk():
    scores = compute_similarity_scores([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]])
    assert len(scores) == 2
    assert abs(scores[0] - 1.0) < 1e-9
    assert abs(scores[1] - 0.0) < 1e-9


def test_top_k_returns_highest_scoring_chunk_first():
    query_vector = [1.0, 0.0]
    chunk_vectors = [[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]]
    chunk_texts = ["best", "unrelated", "second best"]
    top_chunks = find_top_k_chunks(query_vector, chunk_vectors, chunk_texts, 3)
    assert top_chunks[0][1] == "best"
    assert top_chunks[1][1] == "second best"
    assert top_chunks[2][1] == "unrelated"


def test_top_k_respects_requested_count():
    query_vector = [1.0, 0.0]
    chunk_vectors = [[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]]
    chunk_texts = ["a", "b", "c"]
    top_chunks = find_top_k_chunks(query_vector, chunk_vectors, chunk_texts, 2)
    assert len(top_chunks) == 2


def test_top_k_rejects_mismatched_chunk_and_text_counts():
    try:
        find_top_k_chunks([1.0, 0.0], [[1.0, 0.0]], ["only text"], 1)
        find_top_k_chunks([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], ["one text"], 1)
    except ValueError:
        return
    raise AssertionError("Expected ValueError when chunk counts do not match")


def test_top_k_rejects_non_positive_result_count():
    try:
        find_top_k_chunks([1.0, 0.0], [[1.0, 0.0]], ["text"], 0)
    except ValueError:
        return
    raise AssertionError("Expected ValueError when number_of_results is zero")
