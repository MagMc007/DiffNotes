"""OpenRouter provider (OpenAI-compatible API)."""

import os
from dotenv import load_dotenv

from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from ..errors import ProviderAuthError, ProviderError

BASE_URL = "https://openrouter.ai/api/v1"

load_dotenv()

class OpenRouterProvider:
    def __init__(
        self,
        model: str = "nvidia/nemotron-3-ultra-550b-a55b:free",
        timeout: float = 60.0,
    ):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ProviderAuthError("OPENROUTER_API_KEY is not set")
        self._client = OpenAI(api_key=api_key, base_url=BASE_URL, timeout=timeout)
        self._model = model

    def generate(self, messages: list[dict], schema: dict, temperature: float) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "pr_description",
                        "schema": schema,
                        "strict": True,
                    },
                },
            )
        except AuthenticationError as e:
            raise ProviderAuthError(f"OpenRouter auth error: {e}") from e
        except (RateLimitError, APIConnectionError, APIError) as e:
            raise ProviderError(f"OpenRouter API error: {e}") from e

        return response.choices[0].message.content