"""Environment variable validation."""

import os

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "JWT_SECRET_KEY",
]


class EnvValidationError(Exception):
    pass


def validate_env() -> None:
    """Validate that required environment variables are set."""
    missing: list[str] = []
    empty: list[str] = []

    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if value is None:
            missing.append(var)
        elif value.strip() == "":
            empty.append(var)

    errors: list[str] = []
    if missing:
        errors.append(f"Missing required env vars: {', '.join(missing)}")
    if empty:
        errors.append(f"Empty required env vars: {', '.join(empty)}")

    if errors:
        raise EnvValidationError("; ".join(errors))
