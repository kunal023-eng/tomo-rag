import numpy


def cosine_similarity(vector_a, vector_b):
    array_a = numpy.array(vector_a, dtype=float)
    array_b = numpy.array(vector_b, dtype=float)
    if array_a.shape != array_b.shape:
        raise ValueError("Vectors must have the same length")

    dot_product = numpy.dot(array_a, array_b)
    magnitude_a = numpy.linalg.norm(array_a)
    magnitude_b = numpy.linalg.norm(array_b)

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")

    return float(dot_product / (magnitude_a * magnitude_b))


def compute_similarity_scores(query_vector, chunk_vectors):
    similarity_scores = []
    for chunk_vector in chunk_vectors:
        score = cosine_similarity(query_vector, chunk_vector)
        similarity_scores.append(score)
    return similarity_scores


def find_top_k_chunks(query_vector, chunk_vectors, chunk_texts, number_of_results):
    if len(chunk_vectors) != len(chunk_texts):
        raise ValueError("Each chunk vector must have a matching chunk text")
    if number_of_results <= 0:
        raise ValueError("number_of_results must be greater than zero")

    similarity_scores = compute_similarity_scores(query_vector, chunk_vectors)

    scored_chunks = []
    for index in range(len(similarity_scores)):
        scored_chunks.append((similarity_scores[index], chunk_texts[index]))

    scored_chunks.sort(key=lambda scored_chunk: scored_chunk[0], reverse=True)
    top_chunks = scored_chunks[:number_of_results]
    return top_chunks
