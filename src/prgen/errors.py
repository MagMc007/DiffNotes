"""
Custom exception hierarchy.

"""

class InputError(Exception):
    """Bad user input (empty diff, invalid args) """

    exit_code = 2


class EmptyDiffError(InputError):
    """The diff was empty, or empty after filtering. No API call was made."""
    pass

class ProviderError(Exception):
    """Something went wrong calling the model. Retryable by default."""

    retryable = True


class ProviderAuthError(ProviderError):
    """API key missing or invalid. Retrying will never succeed."""

    retryable = False


class GenerationFailed(Exception):
    """All generation/validation attempts failed. Exit code 1."""

    exit_code = 1