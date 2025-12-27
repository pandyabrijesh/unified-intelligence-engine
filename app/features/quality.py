from ..schemas import QualityResult


class QualityScorer:
    def score(self, text: str) -> QualityResult:
        issues = []
        if len(text) < 10:
            issues.append("too_short")
        if len(text) > 5000:
            issues.append("too_long")
        letters = sum(1 for ch in text if ch.isalpha())
        non_letters = sum(1 for ch in text if not ch.isspace() and not ch.isalpha())
        noise_ratio = non_letters / (letters + 1)
        if noise_ratio > 0.5:
            issues.append("noisy_text")
        score = max(0.0, 1.0 - noise_ratio)
        if "too_short" in issues:
            score *= 0.5
        return QualityResult(score=score, issues=issues)
