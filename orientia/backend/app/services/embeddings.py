"""
Embedding generation for RAG — runs fully locally via sentence-transformers,
so there's no OpenAI cost. Uses a multilingual model since student profiles
and program requirements are in French.

First call downloads the model (~470MB) from Hugging Face and caches it;
after that it runs offline with no network calls and no per-request cost.
"""
from functools import lru_cache
import asyncio
from sentence_transformers import SentenceTransformer
from app.config import get_settings

_settings = get_settings()


@lru_cache
def _get_model() -> SentenceTransformer:
    # paraphrase-multilingual-MiniLM-L12-v2: 384-dim, handles French well,
    # small enough to run on a laptop CPU with no GPU required.
    return SentenceTransformer(_settings.embedding_model)


def _embed_sync(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


async def embed_text(text: str) -> list[float]:
    cleaned = text.replace("\n", " ").strip()
    result = await asyncio.to_thread(_embed_sync, [cleaned])
    return result[0]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch embedding — local inference so batching mainly saves Python
    call overhead rather than API cost, but still worth doing for ingestion."""
    cleaned = [t.replace("\n", " ").strip() for t in texts]
    return await asyncio.to_thread(_embed_sync, cleaned)


def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> list[str]:
    """Simple sliding-window chunker. Good enough for admissions-requirement
    pages, which are short and semi-structured rather than long prose."""
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
