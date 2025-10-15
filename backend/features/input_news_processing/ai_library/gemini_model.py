import datetime
import logging
import os
import pathlib
from typing import cast

import instructor
import structlog
from fastapi import HTTPException
from google import genai
from google.genai import types
from instructor import AsyncInstructor
from tenacity import (
    after_log,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from core.redis_client import redis_client
from features.input_news_processing.ai_library.abstract_model import (
    AbstractAIModel,
    ResponseT,
)

logger = structlog.get_logger()


class GeminiAIModel(AbstractAIModel):
    def __init__(self, api_key: str, model_name: str | None = None):
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro-preview-03-25")
        super().__init__(api_key=api_key, model_name=model_name)
        logger.info(f"GeminiAIModel initialized with model: {model_name}")

    @staticmethod
    def upload_files_gemini(
        files: dict[str, pathlib.Path],
        client: genai.Client,
    ) -> dict[str, types.File]:
        # TODO: Implement caching of already uploaded files in session
        """Uploads a file synchronously and returns the File objects"""
        logger.debug(f"Uploading {len(files)} files to Gemini")
        results: dict[str, types.File] = {}
        for key, file_path in files.items():
            logger.debug(f"Uploading file: {key} from path: {file_path}")
            if not file_path.exists():
                logger.error(f"File path {file_path} not found")
                raise ValueError(f"File path {file_path} not found")
            file_obj = client.files.upload(
                file=str(file_path),
                config=types.UploadFileConfig(
                    display_name=key,
                    mime_type="text/plain"
                )
            )
            logger.info(f"File uploaded successfully: {key}, URI = {file_obj.uri}")
            results[key] = file_obj
        logger.info(f"Successfully uploaded {len(results)} files to Gemini")
        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=120, min=1, max=1200),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
    )
    async def prompt_model(
        self,
        files: dict[str, pathlib.Path],
        response_model: type[ResponseT],
        prompt: str,
    ) -> ResponseT:
        """Prompt model with the query and files, with rate limiting applied.

        Preparation of files is done independently.
        """
        logger.info(f"Prompting Gemini model with {len(files)} files and response model: {response_model.__name__}")

        # Apply rate limiting before making any API calls
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        global_limit_key = f"gemini_global_limit_{today_str}"

        # Check global limit (configurable per day app-wide)
        global_limit = int(os.getenv("GEMINI_GLOBAL_DAILY_LIMIT", "100"))
        global_count = redis_client.get_counter(global_limit_key)
        if global_count >= global_limit:
            logger.warning(f"Global Gemini API daily limit reached: {global_count}/{global_limit}")
            raise HTTPException(
                status_code=429, detail="Daily AI API limit reached app-wide. Please try again tomorrow."
            )

        # Increment counter before making the API call
        redis_client.increment_counter(global_limit_key)

        logger.info(f"Gemini API usage - Global: {global_count + 1}/{global_limit}")

        gemini_client = self.prepare_model_sdk()
        client = genai.Client(api_key=self.api_key)
        gemini_files = self.upload_files_gemini(files=files, client=client)

        # Build content list - pass file objects directly
        content_parts = [prompt]
        content_parts.extend(gemini_files.values())  # Add file objects directly

        logger.info("Sending request to Gemini model")
        logger.debug(f"Content to gemini: {content_parts}")
        messages = [{"role": "user", "content": content_parts}]

        result = await gemini_client.chat.completions.create(
            response_model=response_model,
            messages=messages,
        )
        typed_result: ResponseT = cast(ResponseT, result)
        logger.info("Successfully received response from Gemini model")
        return typed_result

    def prepare_model_sdk(self) -> AsyncInstructor:
        """Prepares model encapsulated by instructor library for structured output."""
        logger.info("Preparing Gemini model SDK with instructor")
        instructor_client = instructor.from_provider(
            f"google/{self.model_name}",
            api_key=self.api_key,
        )
        logger.info("Gemini model SDK prepared successfully")
        return cast(AsyncInstructor, instructor_client)