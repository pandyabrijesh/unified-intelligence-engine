from typing import Dict

from ..schemas import IntentResult
from .text_match import count_keyword_matches


INTENT_KEYWORDS = {
    "complaint": ["complain", "issue", "problem", "bad service", "શિકાયત", "शिकायत"],
    "incident_report": ["accident", "fire", "robbery", "attack", "દુર્ઘટના", "आग"],
    "praise": ["thanks", "thank you", "great job", "ઉત્તમ કામ", "शुक्रिया"],
    "question": ["?", "how", "what", "why", "કેમ", "શા માટે", "कैसे", "क्यों"],
    "spam": ["buy now", "discount", "offer", "કુપન", "ऑफ़र"],
}


class IntentAnalyzer:
    def analyze(self, text: str, source: str, domain: str, language: str) -> IntentResult:
        scores: Dict[str, float] = {
            intent: float(count_keyword_matches(text, words))
            for intent, words in INTENT_KEYWORDS.items()
        }

        total = sum(scores.values())
        if total <= 0:
            return IntentResult(
                label="unknown",
                scores={k: 0.0 for k in INTENT_KEYWORDS},
            )

        for key in scores:
            scores[key] /= total

        label = max(scores, key=scores.get)
        return IntentResult(label=label, scores=scores)