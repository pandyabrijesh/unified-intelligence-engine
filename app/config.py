import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


_ENV_LOADED = False
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def load_env_once() -> None:
    """Load repo-level .env values once without overriding real environment vars."""
    global _ENV_LOADED

    if _ENV_LOADED:
        return

    if load_dotenv is not None:
        load_dotenv(dotenv_path=_ENV_PATH, override=False)
    elif _ENV_PATH.is_file():
        for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("export "):
                line = line[len("export ") :].strip()

            key, separator, value = line.partition("=")
            key = key.strip()
            if separator and key and key not in os.environ:
                os.environ[key] = value.strip().strip("'\"")

    _ENV_LOADED = True


def get_env_bool(name: str, default: bool) -> bool:
    load_env_once()
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def get_env_float(
    name: str,
    default: float,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    load_env_once()
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default

    if min_value is not None and parsed < min_value:
        return default
    if max_value is not None and parsed > max_value:
        return default
    return parsed
