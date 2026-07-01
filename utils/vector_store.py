"""
FAISS vector store manager for AI Study Companion.
Handles index creation, persistence, and similarity search
without any LangChain dependency.
"""

import os
import json
import numpy as np
import faiss
from utils.ai_engine import get_embeddings

# Base directory for storing FAISS indices
VECTORSTORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vectorstore")


def _get_index_dir(user_id: int, doc_id: int) -> str:
    """Get the directory path for a specific user+document index."""
    return os.path.join(VECTORSTORE_DIR, str(user_id), str(doc_id))


def create_index(chunks: list[str], user_id: int, doc_id: int) -> bool:
    """
    Create a FAISS index from text chunks and save it to disk.

    Args:
        chunks: List of text chunks to embed and index.
        user_id: User ID for directory organization.
        doc_id: Document ID for directory organization.

    Returns:
        True if index was created successfully, False otherwise.
    """
    if not chunks:
        return False

    try:
        # Generate embeddings for all chunks
        embeddings = get_embeddings(chunks)
        if not embeddings:
            return False

        # Convert to numpy array
        vectors = np.array(embeddings, dtype=np.float32)

        # Create FAISS index (using L2 distance)
        dimension = vectors.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)

        # Create directory and save
        index_dir = _get_index_dir(user_id, doc_id)
        os.makedirs(index_dir, exist_ok=True)

        # Save FAISS index
        faiss.write_index(index, os.path.join(index_dir, "index.faiss"))

        # Save chunks mapping (so we can retrieve the original text)
        with open(os.path.join(index_dir, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error creating FAISS index: {e}")
        return False


def load_index(user_id: int, doc_id: int) -> tuple[faiss.Index | None, list[str] | None]:
    """
    Load a FAISS index and its associated chunks from disk.

    Returns:
        Tuple of (faiss_index, chunks_list) or (None, None) if not found.
    """
    index_dir = _get_index_dir(user_id, doc_id)
    index_path = os.path.join(index_dir, "index.faiss")
    chunks_path = os.path.join(index_dir, "chunks.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        return None, None

    try:
        index = faiss.read_index(index_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        return index, chunks
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None, None


def search(query: str, user_id: int, doc_id: int, k: int = 5) -> list[str]:
    """
    Search the FAISS index for the most relevant chunks to a query.

    Args:
        query: The search query text.
        user_id: User ID for locating the index.
        doc_id: Document ID for locating the index.
        k: Number of results to return.

    Returns:
        List of the most relevant text chunks, ordered by similarity.
    """
    index, chunks = load_index(user_id, doc_id)
    if index is None or chunks is None:
        return []

    try:
        # Generate embedding for the query
        query_embedding = get_embeddings([query])
        if not query_embedding:
            return []

        query_vector = np.array(query_embedding, dtype=np.float32)

        # Search the index
        k = min(k, len(chunks))  # Don't request more results than we have
        distances, indices = index.search(query_vector, k)

        # Return the matching chunks
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(chunks):
                results.append(chunks[idx])

        return results

    except Exception as e:
        print(f"Error searching FAISS index: {e}")
        return []


def index_exists(user_id: int, doc_id: int) -> bool:
    """Check if a FAISS index exists for a given user and document."""
    index_dir = _get_index_dir(user_id, doc_id)
    return (
        os.path.exists(os.path.join(index_dir, "index.faiss"))
        and os.path.exists(os.path.join(index_dir, "chunks.json"))
    )


def delete_index(user_id: int, doc_id: int):
    """Delete the FAISS index for a given user and document."""
    import shutil
    index_dir = _get_index_dir(user_id, doc_id)
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
