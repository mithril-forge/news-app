import pathlib
from typing import cast

import instructor
from instructor import AsyncInstructor
from openai import AsyncOpenAI

from features.input_news_processing.ai_library.abstract_model import (
    AbstractAIModel,
    ResponseT,
)


class OpenAIModel(AbstractAIModel):
    """
    Implementation of AbstractAIModel for ChatGPT using the OpenAI API.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        """
        Initialize the ChatGPT model.

        Args:
            api_key: OpenAI API key
            model_name: Model name to use (default is gpt-4o)
        """
        super().__init__(api_key=api_key, model_name=model_name)

    async def prompt_model(
        self,
        files: dict[str, pathlib.Path],
        response_model: type[ResponseT],
        prompt: str,
    ) -> ResponseT | None:
        """
        Prompt the model with a query and files, returning structured output.

        Args:
            files: Dictionary of file name to file path
            response_model: Pydantic model to structure the response
            prompt: Text prompt to send to the model

        Returns:
            Structured response as specified by response_model
        """
        client = self.prepare_model_sdk()
        for key, value in files.items():
            await client.files.create(file=value, purpose="user_data")

        # Use instructor to get structured output
        result = await client.chat.completions.create(  # type: ignore[type-var]
            response_model=response_model,
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

        return cast(ResponseT, result)

    def prepare_model_sdk(self) -> AsyncInstructor:
        """
        Prepares model encapsulated by instructor library for structured output.

        Returns:
            AsyncInstructor client configured for ChatGPT
        """
        client = AsyncOpenAI(api_key=self.api_key)

        instructor_client = instructor.from_openai(client=client, mode=instructor.Mode.JSON)

        return instructor_client
