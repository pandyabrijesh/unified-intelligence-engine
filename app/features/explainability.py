from typing import List
from ..schemas import ExplainabilityResult, SentimentResult
# reuse lexicons from simple sentiment surrogate if needed
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "happy", "love", "awesome", "satisfied",
    "ઉત્તમ", "સારું", "ખુશ", "મજા", "સારા",
    "अच्छा", "उत्कृष्ट", "खुश", "प्रसन्न", "पसंद"
}
NEGATIVE_WORDS = {
    "bad", "terrible", "worst", "angry", "sad", "hate", "horrible", "disappointed",
    "ખરાબ", "નરસું", "ગુસ્સો", "ભયંકર", "અસંતુષ્ટ",
    "बुरा", "खराब", "नफ़रत", "गुस्सा", "भयानक"
}


class ExplainabilityEngine:
    def explain(self, text: str, sentiment: SentimentResult) -> ExplainabilityResult:
        lower = text.lower()
        pos_terms: List[str] = [w for w in POSITIVE_WORDS if w in lower]
        neg_terms: List[str] = [w for w in NEGATIVE_WORDS if w in lower]
        if sentiment.label.startswith("positive"):
            rationale = "Detected positive sentiment based on: " + ", ".join(pos_terms[:5])
        elif sentiment.label.startswith("negative"):
            rationale = "Detected negative sentiment based on: " + ", ".join(neg_terms[:5])
        else:
            rationale = "Neutral sentiment; few strong polarity cues detected."
        return ExplainabilityResult(
            positive_terms=pos_terms,
            negative_terms=neg_terms,
            rationale=rationale,
        )
