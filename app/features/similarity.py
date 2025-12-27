from typing import Optional
from ..schemas import SimilarityResult


class SimilarityEngine:
    def compare(self, text: str, reference: Optional[str]) -> SimilarityResult:
        # Placeholder; in real use you'd compute cosine similarity vs stored embeddings.
        return SimilarityResult(reference_id=None, similarity=0.0)
