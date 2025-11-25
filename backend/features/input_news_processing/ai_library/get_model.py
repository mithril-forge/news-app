from os import getenv

from features.input_news_processing.ai_library.deepinfra_model import DeepInfraAIModel
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel


def get_ai_model() -> GeminiAIModel | DeepInfraAIModel:
    """Factory method to get the AI model based on environment variable"""

    model_type = getenv("AI_PROVIDER", "gemini").lower()
    if model_type == "gemini":
        return GeminiAIModel()
    elif model_type == "deepinfra":
        return DeepInfraAIModel()
    else:
        raise ValueError(f"Unsupported AI_MODEL_TYPE: {model_type}")
