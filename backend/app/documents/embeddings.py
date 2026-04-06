# backend/app/documents/embeddings.py
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embeddings(
    texts: list[str],
    model: str = "text-embedding-3-small",
) -> list[list[float]]:
    """Generate embeddings for a batch of texts using the OpenAI Embeddings API.

    Args:
        texts: List of strings to embed. OpenAI accepts up to 2048 inputs per
            request; callers that exceed this should batch externally.
        model: Embedding model name. Defaults to ``text-embedding-3-small``
            (1536 dimensions, cost-effective).

    Returns:
        List of float vectors in the same order as the input texts.

    Example::

        vectors = get_embeddings(["What is RAG?", "Retrieval-Augmented Generation"])
        assert len(vectors) == 2
        assert len(vectors[0]) == 1536
    """
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]
