import re
from typing import Tuple


def normalize_text(text: str) -> str:
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text, flags=re.UNICODE).strip()
    return text


def detect_language_simple(text: str) -> str:
    # Gujarati unicode range
    gujarati_range = any("\u0A80" <= ch <= "\u0AFF" for ch in text)
    # Devanagari for Hindi
    devanagari_range = any("\u0900" <= ch <= "\u097F" for ch in text)
    if gujarati_range:
        return "gu"
    if devanagari_range:
        return "hi"
    return "en"


def preprocess(text: str, language: str) -> Tuple[str, str]:
    norm = normalize_text(text)
    lang = language if language != "auto" else detect_language_simple(norm)
    return norm, lang
