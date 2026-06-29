import os
import warnings
from typing import Optional

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoConfig,
    AutoTokenizer,
    XLMRobertaTokenizer,
)

from ..schemas import SentimentResult


DEFAULT_SENTIMENT_MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
UNTRAINED_SENTIMENT_MODEL_NAMES = {"xlm-roberta-base"}


def _resolve_model_name(model_name_or_path: Optional[str]) -> str:
    resolved = (
        model_name_or_path
        or os.getenv("SENTIMENT_MODEL_NAME")
        or DEFAULT_SENTIMENT_MODEL_NAME
    )
    normalized = resolved.strip().lower()

    if normalized in UNTRAINED_SENTIMENT_MODEL_NAMES:
        warnings.warn(
            f"{resolved} is a base checkpoint without a trained sentiment head; "
            f"using {DEFAULT_SENTIMENT_MODEL_NAME} instead.",
            RuntimeWarning,
        )
        return DEFAULT_SENTIMENT_MODEL_NAME

    return resolved


def _normalize_label(label: str) -> str:
    if label is None:
        return "unknown"

    raw = str(label).strip().lower()

    mapping = {
        "label_0": "negative",
        "label_1": "neutral",
        "label_2": "positive",
        "0": "negative",
        "1": "neutral",
        "2": "positive",
        "neg": "negative",
        "neu": "neutral",
        "pos": "positive",
    }

    return mapping.get(raw, raw)


class SentimentAnalyzer:
    """
    HF xlm-roberta sentiment (3-class: negative / neutral / positive).

    IMPORTANT:
    - We avoid fast tokenizers completely for XLM-R models to bypass tokenizer issues.
    - We normalize raw HF labels like LABEL_0/LABEL_1/LABEL_2 into business-friendly labels.
    """

    def __init__(self, model_name_or_path: Optional[str] = None):
        model_name_or_path = _resolve_model_name(model_name_or_path)

        self.model_name_or_path = model_name_or_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ---- TOKENIZER ----
        if "xlm-roberta" in model_name_or_path.lower():
            self.tokenizer = XLMRobertaTokenizer.from_pretrained(model_name_or_path)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name_or_path,
                use_fast=False,
            )

        # ---- MODEL ----
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path
        ).to(self.device)
        self.model.eval()

        # ---- LABEL MAPPING ----
        config: AutoConfig = self.model.config

        if getattr(config, "id2label", None):
            self.id2label = {
                int(k): _normalize_label(v) for k, v in config.id2label.items()
            }
        else:
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
        # label = self.id2label.get(max_id, str(max_id))

        raw_label = str(self.model.config.id2label.get(max_id, str(max_id))) if getattr(self.model.config, "id2label", None) else str(max_id)
        label = self.id2label.get(max_id, str(max_id))

        return SentimentResult(label=label, score=score, raw_label=raw_label)

        # return SentimentResult(label=label, score=score)
