import re
from typing import Dict
from ..schemas import NERResult


LOCATION_HINTS = {"ahmedabad", "vadodara", "surat", "rajkot", "gandhinagar", "mumbai", "delhi"}
ORG_HINTS = {"police", "hospital", "school", "government", "cm office"}


class NERAnalyzer:
    def analyze(self, text: str, language: str) -> NERResult:
        entities: Dict[str, str] = {}
        for token in re.findall(r"[A-Z][a-zA-Z]+", text):
            entities[token] = entities.get(token, "MISC")
        lower = text.lower()
        for loc in LOCATION_HINTS:
            if loc in lower:
                entities[loc] = "LOCATION"
        for org in ORG_HINTS:
            if org in lower:
                entities[org] = "ORG"
        return NERResult(entities=entities)
