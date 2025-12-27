from ..schemas import SummaryResult


class SummaryGenerator:
    def generate(self, text: str, language: str) -> SummaryResult:
        sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sentences:
            return SummaryResult(short="", long="")
        short = sentences[0]
        long = ". ".join(sentences[:2])
        return SummaryResult(short=short, long=long)
