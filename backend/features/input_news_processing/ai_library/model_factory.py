"""
Singleton factory for AI model instances.

This module provides a centralized way to initialize and access AI models,
ensuring that configuration is read once and models are reused throughout the application.
"""

import os
from typing import cast

import structlog

from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
from features.input_news_processing.ai_library.deepinfra_model import DeepInfraModel

logger = structlog.get_logger()


class AIModelFactory:
    """
    Singleton factory for creating and caching AI model instances.

    This ensures that:
    - Environment variables are read once at initialization
    - Model instances are reused across the application
    - Configuration is centralized
    """

    _instance: "AIModelFactory | None" = None
    _deepinfra_model: DeepInfraModel | None = None

    def __new__(cls) -> "AIModelFactory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_deepinfra_model(self) -> DeepInfraModel:
        """
        Get or create the singleton DeepInfra model instance.

        Returns:
            DeepInfraModel: Configured DeepInfra model instance

        Raises:
            ValueError: If DEEPINFRA_API_KEY environment variable is not set
        """
        if self._deepinfra_model is None:
            api_key = os.getenv("DEEPINFRA_API_KEY")
            if api_key is None:
                logger.error("DEEPINFRA_API_KEY environment variable not set")
                raise ValueError("You need to provide DEEPINFRA_API_KEY to use the model.")

            model_name = os.getenv("DEEPINFRA_MODEL_NAME")
            logger.info(f"Initializing singleton DeepInfra model with model: {model_name or 'default'}")
            self._deepinfra_model = DeepInfraModel(api_key=api_key, model_name=model_name)

        return self._deepinfra_model

    def get_default_model(self) -> AbstractAIModel:
        """
        Get the default AI model for the application.

        Currently defaults to DeepInfra, but can be configured to switch
        between different providers based on environment variables.

        Returns:
            AbstractAIModel: The default AI model instance
        """
        return cast(AbstractAIModel, self.get_deepinfra_model())


# Convenience function for easy access
def get_ai_model() -> AbstractAIModel:
    """
    Get the default AI model instance.

    This is the recommended way to access AI models throughout the application.

    Returns:
        AbstractAIModel: Configured AI model instance

    Example:
        ```python
        from features.input_news_processing.ai_library.model_factory import get_ai_model

        ai_model = get_ai_model()
        result = await ai_model.prompt_model(files=files, response_model=MyModel, prompt=prompt)
        ```
    """
    factory = AIModelFactory()
    return factory.get_default_model()
