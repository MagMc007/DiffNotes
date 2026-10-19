"""Generate and validate a PRDescription from a diff."""

from pydantic import ValidationError

from .errors import GenerationFailed
from .providers.openrouter import OpenRouterProvider
from .schema import PRDescription


def generate_pr_description(
    provider: OpenRouterProvider,
    messages: list[dict],
    temperature: float = 0.2,
    max_attempts: int = 3,
) -> PRDescription:
    """Call the provider, validate the JSON, retry with error feedback."""
    schema = PRDescription.model_json_schema()
    attempts: list[str] = []  # raw outputs, for the final error message

    for attempt in range(1, max_attempts + 1):
        try:
            raw = provider.generate(messages, schema, temperature)
        except Exception as e:
            # Retryable provider errors are handled by the caller/cli;
            if not e.retryable:
                raise  

            if attempt == max_attempts:
                raise GenerationFailed(f"provider failed after {max_attempts} attempts: {e}") from e
            
            continue

        attempts.append(raw)
        try:
            # catch shema and invalid_json failures
            return PRDescription.model_validate_json(raw)
        except ValidationError as e:
            if attempt == max_attempts:
                break

            # Feed the failure back so the model can fix it
            messages = messages + [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": (
                        "Your previous response failed validation:\n"
                        f"{e}\n\n"
                        "Fix it and respond with a single corrected JSON object only."
                    ),
                },
            ]

    raise GenerationFailed(
        f"no valid output after {max_attempts} attempts; last error: {e}"
    )