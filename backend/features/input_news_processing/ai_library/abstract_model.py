import abc
import pathlib
from typing import TypeVar, Type

from instructor import AsyncInstructor

T = TypeVar('T')


class AbstractAIModel(abc.ABC):

    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    @abc.abstractmethod
    async def prompt_model(self, files: dict[str, pathlib.Path], response_model: Type[T], prompt: str) -> T:
        """ Prompt model with files and prompt, returns result as the passed type, this is ensured by AsyncInstructor"""
        pass

    @abc.abstractmethod
    def prepare_model_sdk(self) -> AsyncInstructor:
        """ Prepares model that can be work with"""
        pass
