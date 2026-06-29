import json
import logging
import os
import re
import warnings

from ..config import load_env_once

warnings.filterwarnings(
    "ignore",
    message=r"[\s\S]*google\.generativeai[\s\S]*",
    category=FutureWarning,
)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

_MODEL = None
_MODEL_NAME = None
_GENERATE_MODEL_NAMES = None
DEFAULT_GEMINI_MODEL_NAME = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL_NAMES = (
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite",
)
logger = logging.getLogger("uvicorn.error")


def _normalize_model_name(model_name: str) -> str:
    model_name = str(model_name or "").strip()
    if model_name.startswith("models/"):
        return model_name[len("models/") :]
    return model_name


def _supports_generate_content(model) -> bool:
    methods = getattr(model, "supported_generation_methods", None) or []
    return "generateContent" in methods


def _discover_generate_models():
    global _GENERATE_MODEL_NAMES

    if _GENERATE_MODEL_NAMES is not None:
        return _GENERATE_MODEL_NAMES

    try:
        names = [
            _normalize_model_name(getattr(model, "name", ""))
            for model in genai.list_models()
            if _supports_generate_content(model)
        ]
    except Exception as exc:
        logger.warning(
            "Could not list Gemini models; using configured/default candidates: %s: %s",
            exc.__class__.__name__,
            str(exc),
        )
        names = []

    _GENERATE_MODEL_NAMES = [name for name in names if name]
    if _GENERATE_MODEL_NAMES:
        logger.info(
            "Gemini generateContent models available: %s",
            ", ".join(_GENERATE_MODEL_NAMES[:10]),
        )
    return _GENERATE_MODEL_NAMES


def _candidate_model_names():
    configured = _normalize_model_name(
        os.getenv("GEMINI_MODEL_NAME", DEFAULT_GEMINI_MODEL_NAME)
    )
    discovered = _discover_generate_models()

    candidates = []
    for model_name in (
        configured,
        *FALLBACK_GEMINI_MODEL_NAMES,
        *discovered,
    ):
        model_name = _normalize_model_name(model_name)
        if model_name and model_name not in candidates:
            candidates.append(model_name)

    supported = [name for name in candidates if not discovered or name in discovered]
    return supported or candidates


def _select_model_name() -> str:
    configured = _normalize_model_name(
        os.getenv("GEMINI_MODEL_NAME", DEFAULT_GEMINI_MODEL_NAME)
    )
    candidates = _candidate_model_names()

    if configured in candidates:
        return configured

    selected = candidates[0]
    logger.warning(
        "Configured Gemini model %s is unavailable for generateContent; using %s",
        configured,
        selected,
    )
    return selected


def _get_model():
    global _MODEL, _MODEL_NAME

    if genai is None:
        raise RuntimeError(
            "google-generativeai is not installed. Install with: python3 -m pip install google-generativeai"
        )

    if _MODEL is None:
        load_env_once()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment or .env")
        genai.configure(api_key=api_key)
        model_name = _select_model_name()
        logger.info(
            "Initializing Gemini client: model=%s api_key_configured=true",
            model_name,
        )
        _MODEL = genai.GenerativeModel(model_name)
        _MODEL_NAME = model_name

    return _MODEL


def gemini_sentiment(text: str):
    global _MODEL_NAME

    model = _get_model()

    prompt = f"""
Analyze the sentiment of the following text.

Return ONLY valid JSON in this exact format:
{{
  "label": "positive",
  "score": 0.0
}}

Allowed labels: positive, neutral, negative

Text:
{text}
"""

    response = model.generate_content(prompt)
    content = (response.text or "").strip()

    content = re.sub(r"^```json\s*", "", content)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    data = json.loads(content)
    label = str(data.get("label", "neutral")).strip().lower()
    score = float(data.get("score", 0.5))

    if label not in {"positive", "neutral", "negative"}:
        label = "neutral"

    if score < 0.0:
        score = 0.0
    elif score > 1.0:
        score = 1.0

    return {
        "label": label,
        "score": score,
        "model": _MODEL_NAME,
    }
