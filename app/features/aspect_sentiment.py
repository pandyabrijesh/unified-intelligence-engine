from typing import Dict
from ..schemas import AspectSentimentResult
from .sentiment import SentimentAnalyzer


PRODUCT_ASPECTS = ["price", "service", "quality", "delivery", "battery", "camera", "safety"]


class AspectSentimentAnalyzer:
    def __init__(self):
        self._sentiment = SentimentAnalyzer()

    def analyze(self, text: str, domain: str, language: str) -> AspectSentimentResult:
        aspects: Dict[str, str] = {}
        lower = text.lower()
        for aspect in PRODUCT_ASPECTS:
            if aspect in lower:
                sent = self._sentiment.analyze(text, language)
                aspects[aspect] = sent.label
        return AspectSentimentResult(aspects=aspects)
