"""LLM configuration for LM Studio integration."""

import logging
from typing import Optional

from llama_index.core.llms import LLM
from llama_index.llms.openai_like import OpenAILike

from backend.config.settings import settings

logger = logging.getLogger(__name__)


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> LLM:
    """Get configured LLM instance.

    Args:
        model: Model name (default: from settings)
        temperature: Temperature for generation (default: from settings)
        max_tokens: Max tokens for response (default: from settings)

    Returns:
        LlamaIndex LLM instance
    """
    model = model or settings.lm_studio_model
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens or settings.llm_max_tokens

    logger.info(f"Initializing LLM: {model} at {settings.lm_studio_base_url}")

    llm = OpenAILike(
        api_base=settings.lm_studio_base_url,
        api_key=settings.lm_studio_api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        is_chat_model=True,
        timeout=120.0,
    )

    return llm


def test_llm_connection() -> dict[str, any]:
    """Test LLM connection.

    Returns:
        Dictionary with connection status:
        {
            "success": bool,
            "message": str,
            "model": str (if successful)
        }
    """
    try:
        llm = get_llm()

        # Try a simple completion
        response = llm.complete("Hello")

        return {
            "success": True,
            "message": "LLM connection successful",
            "model": settings.lm_studio_model,
            "response_preview": str(response)[:100],
        }
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
        }
