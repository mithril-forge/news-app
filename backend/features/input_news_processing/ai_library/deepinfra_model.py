import datetime
import logging
import os
import pathlib
from typing import cast

import instructor  # type: ignore
import structlog
from fastapi import HTTPException
from instructor import AsyncInstructor
from openai import AsyncOpenAI
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


class DeepInfraModel(AbstractAIModel):
    def __init__(self, api_key: str, model_name: str | None = None):
        if model_name is None:
            model_name = os.getenv("DEEPINFRA_MODEL_NAME", "meta-llama/Meta-Llama-3.1-70B-Instruct")
        super().__init__(api_key=api_key, model_name=model_name)
        logger.info(f"DeepInfraModel initialized with model: {model_name}")

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
        wait=wait_exponential(multiplier=1, min=4, max=10),
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
        System prompt is the prompt parameter, user content is the file contents.
        """
        logger.info(f"Prompting DeepInfra model with {len(files)} files and response model: {response_model.__name__}")

        # Apply rate limiting before making any API calls
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        global_limit_key = f"deepinfra_global_limit_{today_str}"

        # Check global limit (configurable per day app-wide)
        global_limit = int(os.getenv("DEEPINFRA_GLOBAL_DAILY_LIMIT", "100"))
        global_count = redis_client.get_counter(global_limit_key)
        if global_count >= global_limit:
            logger.warning(f"Global DeepInfra API daily limit reached: {global_count}/{global_limit}")
            raise HTTPException(
                status_code=429, detail="Daily AI API limit reached app-wide. Please try again tomorrow."
            )

        # Increment counter before making the API call
        redis_client.increment_counter(global_limit_key)

        logger.info(f"DeepInfra API usage - Global: {global_count + 1}/{global_limit}")

        deepinfra_client = self.prepare_model_sdk()

        # Read file contents directly
        file_contents = self.read_files_as_content(files=files)

        # Build user content with file contents embedded as text
        content_parts = []

        # Add each file's content with a header to identify it
        for filename, content in file_contents.items():
            file_section = f"\n\n--- File: {filename} ---\n{content}\n--- End of {filename} ---\n"
            content_parts.append(file_section)

        # Combine all parts into a single string
        user_content = "".join(content_parts)

        # Get generation parameters from environment
        max_tokens = int(os.getenv("DEEPINFRA_MAX_TOKENS", "8192"))
        temperature = float(os.getenv("DEEPINFRA_TEMPERATURE", "0.8"))
        top_p = float(os.getenv("DEEPINFRA_TOP_P", "0.95"))
        top_k = int(os.getenv("DEEPINFRA_TOP_K", "64"))
        frequency_penalty = float(os.getenv("DEEPINFRA_FREQUENCY_PENALTY", "0.3"))
        presence_penalty = float(os.getenv("DEEPINFRA_PRESENCE_PENALTY", "0.1"))

        logger.info(
            "Sending request to DeepInfra API",
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        logger.debug(f"System prompt length: {len(prompt)} chars, User content length: {len(user_content)} chars")

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]

        result = await deepinfra_client.chat.completions.create(
            model=self.model_name,
            response_model=response_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        typed_result: ResponseT = cast(ResponseT, result)
        logger.info(f"Successfully received response from DeepInfra model: {self.model_name}")
        return typed_result

    def prepare_model_sdk(self) -> AsyncInstructor:
        """Prepares model encapsulated by instructor library for structured output."""
        logger.info("Preparing DeepInfra model SDK with instructor")

        # DeepInfra uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepinfra.com/v1/openai"
        )

        instructor_client = instructor.from_openai(client=client, mode=instructor.Mode.JSON)
        logger.info("DeepInfra model SDK prepared successfully")
        return cast(AsyncInstructor, instructor_client)
