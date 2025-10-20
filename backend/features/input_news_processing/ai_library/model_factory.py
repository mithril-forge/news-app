import os

import structlog

from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
from features.input_news_processing.ai_library.deepinfra_model import DeepInfraModel
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel

logger = structlog.get_logger()


def get_ai_model() -> AbstractAIModel:
    """
    Factory function to get the configured AI model based on LLM_METHOD env var.

    Supported methods:
    - gemini: Uses Google Gemini API (requires GEMINI_API_KEY)
    - deepinfra: Uses DeepInfra API (requires DEEPINFRA_API_KEY)

    Returns:
        AbstractAIModel: Configured AI model instance

    Raises:
        ValueError: If LLM_METHOD is not set or API key is missing
    """
    llm_method = os.getenv("LLM_METHOD", "gemini").lower()
    logger.info(f"Initializing AI model with method: {llm_method}")

    if llm_method == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            logger.error("GEMINI_API_KEY environment variable not set")
            raise ValueError("You need to provide GEMINI_API_KEY to use the Gemini model.")
        return GeminiAIModel(api_key=api_key)

    elif llm_method == "deepinfra":
        api_key = os.getenv("DEEPINFRA_API_KEY")
        if api_key is None:
            logger.error("DEEPINFRA_API_KEY environment variable not set")
            raise ValueError("You need to provide DEEPINFRA_API_KEY to use the DeepInfra model.")
        return DeepInfraModel(api_key=api_key)

    else:
        logger.error(f"Unknown LLM_METHOD: {llm_method}")
        raise ValueError(f"Unknown LLM_METHOD: {llm_method}. Supported values: gemini, deepinfra")
