from ..schemas import ConfidenceResult, SentimentResult, QualityResult


class ConfidenceScorer:
    def score(self, text: str, quality: QualityResult, sentiment: SentimentResult) -> ConfidenceResult:
        reasons = []
        score = 0.5
        if quality.score < 0.3:
            score -= 0.2
            reasons.append("low_quality_text")
        if len(text) < 20:
            score -= 0.2
            reasons.append("very_short_text")
        if sentiment.label == "neutral" and sentiment.score < 0.3:
            score -= 0.1
            reasons.append("weak_sentiment_signal")
        else:
            score += 0.1
        score = max(0.0, min(1.0, score))
        return ConfidenceResult(score=score, reasons=reasons)
