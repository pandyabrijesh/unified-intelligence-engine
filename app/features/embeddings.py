import hashlib
from ..schemas import EmbeddingResult


class EmbeddingEngine:
    def embed(self, text: str, language: str) -> EmbeddingResult:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [b / 255.0 for b in h[:16]]
        return EmbeddingResult(vector=vector)
