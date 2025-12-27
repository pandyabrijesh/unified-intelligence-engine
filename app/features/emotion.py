from typing import Dict
from ..schemas import EmotionResult


EMOTION_LEXICON = {
    "anger": ["angry", "furious", "rage", "ગુસ્સો", "गुस्सा"],
    "fear": ["afraid", "scared", "terror", "ભય", "डर"],
    "joy": ["happy", "joy", "delighted", "ખુશી", "खुशी"],
    "sadness": ["sad", "sorrow", "દુખ", "उदास"],
    "surprise": ["surprised", "shocked", "આશ્ચર્ય", "आश्चर्य"],
}


class EmotionAnalyzer:
    def analyze(self, text: str, language: str) -> EmotionResult:
        lower = text.lower()
        scores: Dict[str, float] = {}
        for emo, words in EMOTION_LEXICON.items():
            scores[emo] = float(sum(lower.count(w) for w in words))
        total = sum(scores.values()) or 1.0
        for k in scores:
            scores[k] /= total
        label = max(scores, key=scores.get) if scores else "neutral"
        return EmotionResult(label=label, scores=scores)
