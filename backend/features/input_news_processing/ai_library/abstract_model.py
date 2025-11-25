import abc
import pathlib
from typing import TypeVar

from instructor import AsyncInstructor  # type: ignore[import-untyped]

ResponseT = TypeVar("ResponseT")


class AbstractAIModel(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    async def prompt_model(
        self,
        files: dict[str, pathlib.Path],
        response_model: type[ResponseT],
        prompt: str,
    ) -> ResponseT | None:
        """Prompt model with files and prompt, returns result as the passed type, this is ensured by AsyncInstructor"""
        pass

    @abc.abstractmethod
    def prepare_model_sdk(self) -> AsyncInstructor:
        """Prepares model that can be work with"""
        pass
