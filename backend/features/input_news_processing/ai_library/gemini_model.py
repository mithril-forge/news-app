import datetime
import logging
import os
import pathlib
from typing import cast

import instructor  # type: ignore
import structlog
from fastapi import HTTPException
from instructor import AsyncInstructor
from tenacity import (
    after_log,
    before_log,
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
    def read_files_as_content(files: dict[str, pathlib.Path]) -> dict[str, str]:
        """Reads files and returns their content as strings."""
        logger.debug(f"Reading {len(files)} files as direct content")
        results: dict[str, str] = {}
        for key, file_path in files.items():
            logger.debug(f"Reading file: {key} from path: {file_path}")
            if not file_path.exists():
                logger.error(f"File path {file_path} not found")
                raise ValueError(f"File path {file_path} not found")

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                results[key] = content
                logger.info(f"File read successfully: {key}, length: {len(content)} chars")
            except Exception as e:
                logger.error(f"Error reading file {key}: {e}")
                raise

        logger.info(f"Successfully read {len(results)} files")
        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=120, min=1, max=1200),
        before_sleep=before_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
    )
    async def prompt_model(
        self,
        files: dict[str, pathlib.Path],
        response_model: type[ResponseT],
        prompt: str,
    ) -> ResponseT:
        """Prompt model with the query and files, with rate limiting applied.

        File contents are read and passed directly as text.
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

        # Read file contents directly instead of uploading
        file_contents = self.read_files_as_content(files=files)

        # Build content with file contents embedded as text
        content_parts = [prompt]

        # Add each file's content with a header to identify it
        for filename, content in file_contents.items():
            file_section = f"\n\n--- File: {filename} ---\n{content}\n--- End of {filename} ---\n"
            content_parts.append(file_section)

        # Combine all parts into a single string
        combined_content = "".join(content_parts)

        logger.info("Sending request to Gemini model")
        logger.debug(f"Combined content length: {len(combined_content)} chars")
        messages = [{"role": "user", "content": combined_content}]

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

        instructor_client = instructor.from_provider(f"google/{self.model_name}", api_key=self.api_key, use_async=True)
        logger.info("Gemini model SDK prepared successfully")
        return cast(AsyncInstructor, instructor_client)
