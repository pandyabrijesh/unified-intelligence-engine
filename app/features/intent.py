from typing import Dict
from ..schemas import IntentResult


INTENT_KEYWORDS = {
    "complaint": ["complain", "issue", "problem", "bad service", "શિકાયત", "शिकायत"],
    "incident_report": ["accident", "fire", "robbery", "attack", "દુર્ઘટના", "आग"],
    "praise": ["thanks", "thank you", "great job", "ઉત્તમ કામ", "शुक्रिया"],
    "question": ["?", "how", "what", "why", "કેમ", "શા માટે", "कैसे", "क्यों"],
    "spam": ["buy now", "discount", "offer", "કુપન", "ऑफ़र"],
}


class IntentAnalyzer:
    def analyze(self, text: str, source: str, domain: str, language: str) -> IntentResult:
        lower = text.lower()
        scores: Dict[str, float] = {k: 0.0 for k in INTENT_KEYWORDS}
        for intent, words in INTENT_KEYWORDS.items():
            scores[intent] = float(sum(lower.count(w) for w in words))
        total = sum(scores.values()) or 1.0
        for k in scores:
            scores[k] /= total
        label = max(scores, key=scores.get) if scores else "unknown"
        return IntentResult(label=label, scores=scores)
