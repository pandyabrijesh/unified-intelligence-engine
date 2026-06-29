from typing import Optional

from ..schemas import IncidentResult
from .text_match import count_keyword_matches


INCIDENT_KEYWORDS = {
    "road_accident": ["accident", "crash", "collision", "bus overturned", "દુર્ઘટના", "टक्कर"],
    "fire": ["fire", "burning", "blaze", "આગ", "जल रही"],
    "crime": ["murder", "robbery", "assault", "attack", "हत्या", "ચોરી", "हमला"],
    "protest": ["protest", "rally", "strike", "ધરણા", "हड़ताल"],
    "other": ["incident", "violence", "riot", "તોડફોડ", "दंगा"],
}


class IncidentAnalyzer:
    def analyze(self, text: str, source: str, domain: str, language: str) -> IncidentResult:
        lower = text.lower()

        best_cat: Optional[str] = None
        best_score = 0

        for cat, words in INCIDENT_KEYWORDS.items():
            score = count_keyword_matches(text, words)
            if score > best_score:
                best_score = score
                best_cat = cat

        is_incident = best_score > 0 or domain == "incident"

        severity = None
        if is_incident:
            if any(w in lower for w in ["death", "dead", "મૃત્યુ", "मृत"]):
                severity = "high"
            elif any(w in lower for w in ["injured", "ઘાયલ", "घायल"]):
                severity = "medium"
            else:
                severity = "low"

        return IncidentResult(
            is_incident=is_incident,
            category=best_cat,
            severity=severity,
        )