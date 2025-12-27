import re
from ..schemas import SpamResult


URL_RE = re.compile(r"https?://\S+")
REPEAT_RE = re.compile(r"(.)\1{4,}")


class SpamDetector:
    def analyze(self, text: str, source: str) -> SpamResult:
        reasons = []
        if len(URL_RE.findall(text)) >= 2:
            reasons.append("many_links")
        if "buy now" in text.lower():
            reasons.append("buy_now_phrase")
        if REPEAT_RE.search(text):
            reasons.append("repeated_characters")
        return SpamResult(is_spam=len(reasons) > 0, reasons=reasons)
