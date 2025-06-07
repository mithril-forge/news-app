import pathlib
from typing import TypeVar, Generic, Type, Union

import instructor
from instructor import AsyncInstructor

from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
import google.generativeai as genai
from core.logger import create_logger

T = TypeVar('T')

logger = create_logger(__name__)


class GeminiAIModel(AbstractAIModel, Generic[T]):

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro-preview-03-25"):
        super().__init__(api_key=api_key, model_name=model_name)
        logger.info(f"GeminiAIModel initialized with model: {model_name}")

    @staticmethod
    def upload_files_gemini(files: dict[str, pathlib.Path]) -> dict[str, genai.types.File]:
        # TODO: Implement caching of already uploaded files in session
        """Uploads a file synchronously and returns the File objects"""
        logger.debug(f"Uploading {len(files)} files to Gemini")
        results: dict[str, genai.types.File] = {}
        for key, file_path in files.items():
            logger.debug(f"Uploading file: {key} from path: {file_path}")
            if not file_path.exists():
                logger.error(f"File path {file_path} not found")
                raise ValueError(f"File path {file_path} not found")
            file_obj = genai.upload_file(path=file_path, display_name=key, mime_type='text/plain')
            logger.info(f"File uploaded successfully: {key}, URI = {file_obj.uri}")
            results[key] = file_obj
        logger.info(f"Successfully uploaded {len(results)} files to Gemini")
        return results

    async def prompt_model(self, files: dict[str, pathlib.Path], response_model: Type[T], prompt: str) -> T:
        """ Prompt model with the query and files, the preparation of files is done independently"""
        logger.info(f"Prompting Gemini model with {len(files)} files and response model: {response_model.__name__}")
        contents: list[Union[str, genai.types.File]] = [prompt]
        gemini_client = self.prepare_model_sdk()
        gemini_files = self.upload_files_gemini(files=files)
        contents.extend(gemini_files.values())

        logger.debug("Sending request to Gemini model")
        result = await gemini_client.chat.completions.create(response_model=response_model,
                                                             messages=[{"role": "user", "content": contents}])
        logger.info(f"Successfully received response from Gemini model")
        return result

    def prepare_model_sdk(self) -> AsyncInstructor:
        """ Prepares model encapsulated by instructor library for structured output."""
        logger.debug("Preparing Gemini model SDK with instructor")
        genai.configure(api_key=self.api_key)
        client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=self.model_name
            ),
            mode=instructor.Mode.GEMINI_JSON,
            use_async=True
        )
        logger.info("Gemini model SDK prepared successfully")
        return client