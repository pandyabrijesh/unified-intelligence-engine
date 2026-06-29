import re
from typing import List


_SPLIT_PATTERN = r"[\s,.;:!?()\[\]{}\"'“”‘’\-_/|]+"


def _tokenize(text: str) -> List[str]:
    return [tok for tok in re.split(_SPLIT_PATTERN, text.lower()) if tok]


def count_keyword_matches(text: str, keywords: List[str]) -> int:
    """
    Safer keyword matcher to avoid substring false positives.

    Examples:
    - Prevents Gujarati 'રન' from matching inside 'કરનાર'
    - Preserves multi-word phrase matching like 'bad service'
    """
    lowered = text.lower()
    tokens = _tokenize(lowered)
    total = 0

    for kw in keywords:
        kw = kw.strip().lower()
        if not kw:
            continue

        # Multi-word phrase: match exact escaped phrase in text
        if " " in kw:
            total += len(re.findall(re.escape(kw), lowered))
            continue

        # ASCII/Latin token: use proper word boundary
        if re.fullmatch(r"[a-z0-9_]+", kw):
            pattern = r"\b" + re.escape(kw) + r"\b"
            total += len(re.findall(pattern, lowered))
            continue

        # Non-Latin token: compare token-by-token to avoid substring matching
        total += sum(1 for token in tokens if token == kw)

    return total