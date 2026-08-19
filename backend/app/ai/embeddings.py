"""AI capabilities built on LangChain + LangGraph with BGE embeddings.

The heavy AI dependencies live in the optional ``ai`` extra group and are
installed with::

    uv sync --extra ai

Embeddings use the BGE family of models (``BAAI/bge-small-en-v1.5`` by
default), which produce strong dense embeddings for semantic search and RAG.
"""

from functools import lru_cache

BGE_MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache
def get_embeddings():
    """Return a cached BGE embedding model via ``langchain-huggingface``."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=BGE_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


async def embed_text(text: str) -> list[float]:
    """Embed a single piece of text into a normalized vector."""
    embeddings = get_embeddings()
    vectors = await embeddings.aembed_query(text)
    return vectors
