import abc
from typing import Any, TypeVar

from instructor import AsyncInstructor
from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class AbstractAIModel(abc.ABC):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    @abc.abstractmethod
    async def prompt(
        self,
        prompt: str,
        response_model: type[ResponseT],
        **context: list[BaseModel] | BaseModel,
    ) -> ResponseT:
        """
        Prompt the AI model with structured context data.

        Args:
            prompt: The text prompt to send to the model
            response_model: Pydantic model defining the expected response structure
            **context: Named arguments of Pydantic models or lists to include as context

        Returns:
            Structured response as defined by response_model

        Example:
            ```python
            result = await model.prompt(
                prompt="Analyze these articles",
                response_model=AnalysisResult,
                articles=article_list,
                tags=tag_list,
            )
            ```
        """
        pass

    @abc.abstractmethod
    def prepare_model_sdk(self) -> AsyncInstructor:
        """Prepares the underlying model SDK for use with instructor"""
        pass
