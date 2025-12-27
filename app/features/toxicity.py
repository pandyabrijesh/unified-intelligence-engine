from ..schemas import ToxicityResult


TOXIC_WORDS = {
    "idiot", "stupid", "hate", "kill", "bloody",
    "મૂર્ખ", "નાલાયક",
    "मूर्ख", "नफरत", "मार दूँ"
}


class ToxicityAnalyzer:
    def analyze(self, text: str, language: str) -> ToxicityResult:
        lower = text.lower()
        hits = sum(1 for w in TOXIC_WORDS if w in lower)
        score = min(1.0, hits / 3.0)
        return ToxicityResult(is_toxic=hits > 0, score=score)
