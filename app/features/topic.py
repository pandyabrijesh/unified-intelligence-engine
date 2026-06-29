from typing import Dict

from ..schemas import TopicResult
from .text_match import count_keyword_matches


TOPIC_KEYWORDS = {
    "politics": [
        "election",
        "minister",
        "cm",
        "pm",
        "government",
        "મંત્રી",
        "મુખ્યમંત્રી",
        "પ્રધાનમંત્રી",
        "સરકાર",
        "मंत्री",
        "मुख्यमंत्री",
        "प्रधानमंत्री",
        "सरकार",
    ],
    "crime": ["murder", "robbery", "assault", "theft", "ચોરી", "हत्या"],
    "accident": ["accident", "crash", "collision", "દુર્ઘટના", "टक्कर"],
    "business": ["market", "stock", "profit", "loss", "કંપની", "बाज़ार"],
    "sports": ["match", "goal", "cricket", "football", "રમત", "खेल"],
    "entertainment": ["movie", "film", "song", "actor", "ફિલ્મ", "गाना"],
    "generic": [],
}


class TopicAnalyzer:
    def analyze(self, text: str, source: str, domain: str, language: str) -> TopicResult:
        scores: Dict[str, float] = {
            topic: float(count_keyword_matches(text, words))
            for topic, words in TOPIC_KEYWORDS.items()
        }

        if domain == "product":
            scores["business"] += 0.2
        if domain == "incident":
            scores["crime"] += 0.1
            scores["accident"] += 0.1

        total = sum(scores.values())
        if total <= 0:
            return TopicResult(
                label="generic",
                scores={k: 0.0 for k in TOPIC_KEYWORDS},
            )

        for key in scores:
            scores[key] /= total

        label = max(scores, key=scores.get)
        return TopicResult(label=label, scores=scores)