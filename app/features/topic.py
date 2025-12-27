from typing import Dict
from ..schemas import TopicResult


TOPIC_KEYWORDS = {
    "politics": ["election", "minister", "cm", "pm", "કાનૂન", "चुनाव", "सरकार"],
    "crime": ["murder", "robbery", "assault", "theft", "ચોરી", "हत्या"],
    "accident": ["accident", "crash", "collision", "દુર્ઘટના", "टक्कर"],
    "business": ["market", "stock", "profit", "loss", "કંપની", "बाज़ार"],
    "sports": ["match", "goal", "cricket", "football", "રન", "खेल"],
    "entertainment": ["movie", "film", "song", "actor", "ફિલ્મ", "गाना"],
    "generic": [],
}


class TopicAnalyzer:
    def analyze(self, text: str, source: str, domain: str, language: str) -> TopicResult:
        lower = text.lower()
        scores: Dict[str, float] = {k: 0.0 for k in TOPIC_KEYWORDS}
        for topic, words in TOPIC_KEYWORDS.items():
            scores[topic] = float(sum(lower.count(w) for w in words))
        if domain == "product":
            scores["business"] += 0.2
        if domain == "incident":
            scores["crime"] += 0.1
            scores["accident"] += 0.1
        total = sum(scores.values()) or 1.0
        for k in scores:
            scores[k] /= total
        label = max(scores, key=scores.get) if scores else "generic"
        return TopicResult(label=label, scores=scores)
