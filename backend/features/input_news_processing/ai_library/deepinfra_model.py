import datetime
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import cast

import instructor
import structlog
from fastapi import HTTPException
from instructor import AsyncInstructor
from openai import AsyncOpenAI
from pydantic import BaseModel
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


class DeepInfraModel(AbstractAIModel):
    """
    DeepInfra AI Model implementation using OpenAI-compatible API.

    Supports multiple models including:
    - meta-llama/Llama-3.3-70B-Instruct
    - meta-llama/Meta-Llama-3.1-405B-Instruct
    - Qwen/QwQ-32B-Preview
    - mistralai/Mixtral-8x7B-Instruct-v0.1
    """

    def __init__(self, api_key: str, model_name: str | None = None):
        if model_name is None:
            model_name = os.getenv("DEEPINFRA_MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
        super().__init__(api_key=api_key, model_name=model_name)
        logger.info(f"DeepInfraModel initialized with model: {model_name}")

    @staticmethod
    def _serialize_context(**context: list[BaseModel] | BaseModel) -> str:
        """
        Serializes Pydantic models into a formatted string for the AI prompt.

        Args:
            **context: Named arguments of Pydantic models or lists of models

        Returns:
            Formatted string with all context data
        """
        logger.debug(f"Serializing {len(context)} context items")
        content_parts = []

        for key, value in context.items():
            logger.debug(f"Serializing context item: {key}")

            # Handle both single models and lists
            if isinstance(value, list):
                # List of Pydantic models
                data = [model.model_dump() for model in value]
                json_str = json.dumps(data, indent=2, default=str)
                content_parts.append(f"--- {key} ---\n{json_str}\n")
                logger.debug(f"Serialized list of {len(value)} items for {key}")
            else:
                # Single Pydantic model
                json_str = json.dumps(value.model_dump(), indent=2, default=str)
                content_parts.append(f"--- {key} ---\n{json_str}\n")
                logger.debug(f"Serialized single item for {key}")

        combined_content = "\n".join(content_parts)
        logger.info(f"Successfully serialized {len(context)} context items ({len(combined_content)} chars)")
        return combined_content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
    )
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
        """
        logger.info(
            f"Prompting DeepInfra model with {len(context)} context items and response model: {response_model.__name__}"
        )

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

        # Serialize context and combine with prompt
        context_content = self._serialize_context(**context)
        combined_prompt = f"{prompt}\n\n{context_content}"

        deepinfra_client = self.prepare_model_sdk()

        logger.info("Sending request to DeepInfra model")
        logger.debug(f"Combined prompt length: {len(combined_prompt)} chars")
        logger.debug(f"Response model: {response_model}")

        messages = [{"role": "user", "content": combined_prompt}]

        # Call the API - use regular create since create_with_completion doesn't work with list responses
        response = await deepinfra_client.chat.completions.create(  # type: ignore[type-var]
            response_model=response_model,
            model=self.model_name,
            messages=messages,  # type: ignore[arg-type]
        )

        typed_result: ResponseT = cast(ResponseT, response)

        # Log token usage - try to access _raw_response if available
        usage_logged = False
        if hasattr(response, "_raw_response"):
            raw_response = response._raw_response
            if hasattr(raw_response, "usage") and raw_response.usage:
                usage = raw_response.usage
                logger.info(
                    f"DeepInfra API call completed - "
                    f"Input tokens: {usage.prompt_tokens}, "
                    f"Output tokens: {usage.completion_tokens}, "
                    f"Total tokens: {usage.total_tokens}, "
                    f"Model: {self.model_name}"
                )
                usage_logged = True

        if not usage_logged:
            # Fallback: log estimated token counts based on character length (rough: ~4 chars per token)
            estimated_input_tokens = len(combined_prompt) // 4
            # Handle both list and single object responses
            if isinstance(response, list):
                estimated_output_tokens = len(json.dumps([item.model_dump() if hasattr(item, "model_dump") else str(item) for item in response])) // 4
            else:
                estimated_output_tokens = len(json.dumps(response.model_dump() if hasattr(response, "model_dump") else str(response))) // 4
            logger.info(
                f"DeepInfra API call completed - "
                f"Estimated input tokens: ~{estimated_input_tokens}, "
                f"Estimated output tokens: ~{estimated_output_tokens}, "
                f"Model: {self.model_name} "
                f"(actual usage data not available)"
            )

        logger.info("Successfully received response from DeepInfra model")
        return typed_result

    def prepare_model_sdk(self) -> AsyncInstructor:
        """Prepares model encapsulated by instructor library for structured output."""
        logger.info("Preparing DeepInfra model SDK with instructor")

        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )

        # Use MD_JSON mode for better compatibility with DeepInfra
        # This mode uses markdown JSON blocks which works well with most models
        instructor_client = instructor.from_openai(
            client=client,
            mode=instructor.Mode.MD_JSON,
        )

        logger.info("DeepInfra model SDK prepared successfully")
        return cast(AsyncInstructor, instructor_client)
