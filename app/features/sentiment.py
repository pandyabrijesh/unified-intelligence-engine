import os
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from ..schemas import SentimentResult


class SentimentAnalyzer:
    """HF xlm-roberta sentiment (3-class: negative / neutral / positive)."""

    def __init__(self, model_name_or_path: Optional[str] = None):
        # 1) Choose model (env var or default)
        model_name_or_path = (
            model_name_or_path
            or os.getenv("SENTIMENT_MODEL_NAME", "xlm-roberta-base")
        )

        # 2) Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 3) Load tokenizer + model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path
        ).to(self.device)
        self.model.eval()

        # 4) HARD-CODE our own mapping, ignore model.config.id2label
        #    Make sure your fine-tuned model has num_labels = 3
        self.id2label = {
            0: "negative",
            1: "neutral",
            2: "positive",
        }

    def analyze(self, text: str, language: str) -> SentimentResult:
        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )
        encoded = {k: v.to(self.device) for k, v in encoded.items()}

        with torch.no_grad():
            outputs = self.model(**encoded)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1)

        max_id = int(torch.argmax(probs).item())
        score = float(probs[max_id].item())
        label = self.id2label.get(max_id, str(max_id))

        return SentimentResult(label=label, score=score)