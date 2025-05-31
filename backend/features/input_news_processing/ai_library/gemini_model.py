import os
import pathlib
from typing import TypeVar, Generic, Type, Union

import instructor
from instructor import AsyncInstructor
from pydantic import BaseModel

from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
import google.generativeai as genai

T = TypeVar('T')


class GeminiAIModel(AbstractAIModel, Generic[T]):

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro-preview-03-25"):
        super().__init__(api_key=api_key, model_name=model_name)

    @staticmethod
    def upload_files_gemini(files: dict[str, pathlib.Path]) -> dict[str, genai.types.File]:
        # TODO: Implement caching of already uploaded files in session
        """Uploads a file synchronously and returns the File objects"""
        results: dict[str, genai.types.File] = {}
        for key, file_path in files.items():
            if not file_path.exists():
                raise ValueError(f"File path {file_path} not found")
            file_obj = genai.upload_file(path=file_path, display_name=key, mime_type='text/plain')
            print(f"File uploaded successfully: URI = {file_obj.uri}")
            results[key] = file_obj
        return results

    async def prompt_model(self, files: dict[str, pathlib.Path], response_model: Type[T], prompt: str) -> T:
        """ Prompt model with the query and files, the preparation of files is done independently"""
        contents: list[Union[str, genai.types.File]] = [prompt]
        gemini_client = self.prepare_model_sdk()
        gemini_files = self.upload_files_gemini(files=files)
        contents.extend(gemini_files.values())
        result = await gemini_client.chat.completions.create(response_model=response_model,
                                                             messages=[{"role": "user", "content": contents}])
        return result

    def prepare_model_sdk(self) -> AsyncInstructor:
        """ Prepares model encapsulated by instructor library for structured output."""
        genai.configure(api_key=self.api_key)
        client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=self.model_name
            ),
            mode=instructor.Mode.GEMINI_JSON,
            use_async=True
        )
        return client
