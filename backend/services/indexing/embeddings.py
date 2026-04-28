"""Embedding model configuration using HuggingFace."""

import logging
import os
from typing import Optional

# Configure HuggingFace mirror for China - MUST be set before any imports
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.expanduser('~/.cache/huggingface')

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from backend.config.settings import settings

logger = logging.getLogger(__name__)


def get_embedding_model(
    model_name: Optional[str] = None,
    device: str = "cpu",
) -> BaseEmbedding:
    """Get configured embedding model.

    Args:
        model_name: HuggingFace model name (default: from settings)
        device: Device to run on ("cpu" or "cuda")

    Returns:
        LlamaIndex embedding model
    """
    model_name = model_name or settings.embedding_model

    logger.info(f"Loading embedding model: {model_name} on {device}")

    # Try to load from local cache first
    try:
        embed_model = HuggingFaceEmbedding(
            model_name=model_name,
            device=device,
            trust_remote_code=True,
            cache_folder=os.path.expanduser('~/.cache/huggingface'),
        )
        return embed_model
    except Exception as e:
        logger.warning(f"Failed to load from cache, will download: {e}")
        # If local cache fails, download from mirror
        embed_model = HuggingFaceEmbedding(
            model_name=model_name,
            device=device,
            trust_remote_code=True,
        )
        return embed_model


def test_embedding_model() -> dict[str, any]:
    """Test embedding model.

    Returns:
        Dictionary with test status:
        {
            "success": bool,
            "message": str,
            "model": str,
            "embedding_dim": int (if successful)
        }
    """
    try:
        embed_model = get_embedding_model()

        # Test embedding
        test_text = "This is a test sentence."
        embedding = embed_model.get_text_embedding(test_text)

        return {
            "success": True,
            "message": "Embedding model loaded successfully",
            "model": settings.embedding_model,
            "embedding_dim": len(embedding),
        }
    except Exception as e:
        logger.error(f"Embedding model test failed: {e}")
        return {
            "success": False,
            "message": f"Failed to load embedding model: {str(e)}",
        }
