from typing import Dict

from ..schemas import EmotionResult
from .text_match import count_keyword_matches


EMOTION_LEXICON = {
    "anger": ["angry", "furious", "rage", "ગુસ્સો", "गुस्सा"],
    "fear": ["afraid", "scared", "terror", "ભય", "डर"],
    "joy": ["happy", "joy", "delighted", "ખુશી", "खुशी"],
    "sadness": ["sad", "sorrow", "દુખ", "उदास"],
    "surprise": ["surprised", "shocked", "આશ્ચર્ય", "आश्चर्य"],
}


class EmotionAnalyzer:
    def analyze(self, text: str, language: str) -> EmotionResult:
        scores: Dict[str, float] = {
            emo: float(count_keyword_matches(text, words))
            for emo, words in EMOTION_LEXICON.items()
        }

        total = sum(scores.values())
        if total <= 0:
            return EmotionResult(
                label="unknown",
                scores={k: 0.0 for k in EMOTION_LEXICON},
            )

        for key in scores:
            scores[key] /= total

        label = max(scores, key=scores.get)
        return EmotionResult(label=label, scores=scores)