import logging
import time
from typing import Any, Dict, List

from .config import get_env_bool, get_env_float
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ModelInfo,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    SentimentResult,
)
from .text_preprocessor import preprocess
from .features.sentiment import SentimentAnalyzer
from .features.emotion import EmotionAnalyzer
from .features.toxicity import ToxicityAnalyzer
from .features.intent import IntentAnalyzer
from .features.topic import TopicAnalyzer
from .features.incident import IncidentAnalyzer
from .features.ner import NERAnalyzer
from .features.location import LocationResolver
from .features.summary import SummaryGenerator
from .features.aspect_sentiment import AspectSentimentAnalyzer
from .features.similarity import SimilarityEngine
from .features.embeddings import EmbeddingEngine
from .features.spam import SpamDetector
from .features.quality import QualityScorer
from .features.explainability import ExplainabilityEngine
from .features.confidence import ConfidenceScorer
from .features.actions import ActionRecommender
from .features.gemini_sentiment import gemini_sentiment


logger = logging.getLogger("uvicorn.error")


class UnifiedEngine:
    """Single engine instance apps can import."""

    DEFAULT_GEMINI_FALLBACK_THRESHOLD = 0.60

    def __init__(self):
        self.gemini_sentiment_fallback_enabled = get_env_bool(
            "GEMINI_SENTIMENT_FALLBACK_ENABLED",
            True,
        )
        self.gemini_sentiment_fallback_threshold = get_env_float(
            "GEMINI_SENTIMENT_FALLBACK_THRESHOLD",
            get_env_float(
                "GEMINI_FALLBACK_THRESHOLD",
                self.DEFAULT_GEMINI_FALLBACK_THRESHOLD,
                0.0,
                1.0,
            ),
            0.0,
            1.0,
        )
        logger.info(
            "Gemini sentiment fallback config: enabled=%s threshold=%.4f",
            self.gemini_sentiment_fallback_enabled,
            self.gemini_sentiment_fallback_threshold,
        )

        self.sentiment = SentimentAnalyzer()
        self.emotion = EmotionAnalyzer()
        self.toxicity = ToxicityAnalyzer()
        self.intent = IntentAnalyzer()
        self.topic = TopicAnalyzer()
        self.incident = IncidentAnalyzer()
        self.ner = NERAnalyzer()
        self.location = LocationResolver()
        self.summary = SummaryGenerator()
        self.aspect = AspectSentimentAnalyzer()
        self.similarity = SimilarityEngine()
        self.embed = EmbeddingEngine()
        self.spam = SpamDetector()
        self.quality = QualityScorer()
        self.explain = ExplainabilityEngine()
        self.confidence = ConfidenceScorer()
        self.actions = ActionRecommender()

    def analyze_batch(self, batch_req: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
        results: List[AnalyzeResponse] = []
        for item in batch_req.items:
            results.append(self.analyze(item))
        return BatchAnalyzeResponse(items=results)

    def _apply_gemini_fallback(
        self,
        sentiment: SentimentResult,
        text_norm: str,
    ) -> tuple[SentimentResult, Dict[str, Any]]:
        """
        Use Gemini when the original local sentiment score is below threshold.
        Return a fresh Gemini result so local sentiment fields do not leak through.
        """
        original_label = getattr(sentiment, "label", None)
        try:
            local_score = float(getattr(sentiment, "score", 0.0) or 0.0)
        except Exception:
            local_score = 0.0

        diagnostics = {
            "gemini_fallback_enabled": self.gemini_sentiment_fallback_enabled,
            "gemini_fallback_threshold": self.gemini_sentiment_fallback_threshold,
            "gemini_fallback_triggered": False,
            "gemini_fallback_status": "skipped",
            "original_sentiment_label": original_label,
            "original_sentiment_score": local_score,
        }

        if not self.gemini_sentiment_fallback_enabled:
            diagnostics["gemini_fallback_reason"] = "disabled"
            logger.info(
                "Gemini sentiment fallback skipped: disabled original_label=%s original_score=%.4f",
                original_label,
                local_score,
            )
            try:
                setattr(sentiment, "source", "local_model")
            except Exception:
                pass
            return sentiment, diagnostics

        if local_score >= self.gemini_sentiment_fallback_threshold:
            diagnostics["gemini_fallback_reason"] = "score_above_threshold"
            logger.info(
                "Gemini sentiment fallback skipped: original_label=%s original_score=%.4f threshold=%.4f",
                original_label,
                local_score,
                self.gemini_sentiment_fallback_threshold,
            )
            # local model is good enough
            try:
                setattr(sentiment, "source", "local_model")
            except Exception:
                pass
            return sentiment, diagnostics

        diagnostics["gemini_fallback_triggered"] = True
        diagnostics["gemini_fallback_status"] = "triggered"
        diagnostics["gemini_fallback_reason"] = "score_below_threshold"
        logger.info(
            "Gemini sentiment fallback triggered: original_label=%s original_score=%.4f threshold=%.4f",
            original_label,
            local_score,
            self.gemini_sentiment_fallback_threshold,
        )

        try:
            g = gemini_sentiment(text_norm)

            gemini_label = str(g.get("label", "neutral")).strip().lower()
            if gemini_label not in {"positive", "neutral", "negative"}:
                gemini_label = "neutral"

            try:
                gemini_score = float(g.get("score", 0.5))
            except (TypeError, ValueError):
                gemini_score = 0.5
            gemini_score = max(0.0, min(1.0, gemini_score))

            gemini_sentiment_result = SentimentResult(
                label=gemini_label,
                score=gemini_score,
                source="gemini",
            )
            diagnostics.update(
                {
                    "gemini_fallback_status": "succeeded",
                    "gemini_sentiment_label": gemini_label,
                    "gemini_sentiment_score": gemini_score,
                    "gemini_model": g.get("model"),
                }
            )
            logger.info(
                "Gemini sentiment fallback succeeded: gemini_label=%s gemini_score=%.4f",
                gemini_label,
                gemini_score,
            )
            return gemini_sentiment_result, diagnostics

        except Exception as exc:
            diagnostics.update(
                {
                    "gemini_fallback_status": "failed",
                    "gemini_error_type": exc.__class__.__name__,
                    "gemini_error": str(exc)[:300],
                }
            )
            logger.warning(
                "Gemini sentiment fallback failed; using local sentiment: %s: %s",
                exc.__class__.__name__,
                str(exc),
                exc_info=True,
            )
            # keep local result if Gemini fails
            try:
                setattr(sentiment, "source", "local_model_fallback_failed")
            except Exception:
                pass
            return sentiment, diagnostics

    def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        start = time.time()

        text_norm, lang = preprocess(req.text, req.language)

        # 1. sentiment first
        sentiment = self.sentiment.analyze(text_norm, lang)

        # 2. quality is shared by confidence and action logic.
        quality = self.quality.score(text_norm)

        # 3. fallback to Gemini if original local sentiment score is below threshold
        sentiment, gemini_fallback = self._apply_gemini_fallback(sentiment, text_norm)

        # 4. remaining analyzers
        emotion = self.emotion.analyze(text_norm, lang)
        toxicity = self.toxicity.analyze(text_norm, lang)
        intent = self.intent.analyze(text_norm, req.source, req.domain, lang)
        topic = self.topic.analyze(text_norm, req.source, req.domain, lang)
        incident = self.incident.analyze(text_norm, req.source, req.domain, lang)
        ner = self.ner.analyze(text_norm, lang)
        locations = self.location.resolve(ner.entities)
        summary = self.summary.generate(text_norm, lang)
        aspect_sent = self.aspect.analyze(text_norm, req.domain, lang)
        similarity = self.similarity.compare(text_norm, None)
        embedding = self.embed.embed(text_norm, lang)
        spam = self.spam.analyze(text_norm, req.source)

        # recompute downstream logic using final sentiment
        explain = self.explain.explain(text_norm, sentiment)
        confidence = self.confidence.score(text_norm, quality, sentiment)

        action = self.actions.recommend(
            sentiment=sentiment,
            incident=incident,
            toxicity=toxicity,
            intent=intent,
            spam=spam,
            quality=quality,
            domain=req.domain,
            source=req.source,
        )

        latency_ms = (time.time() - start) * 1000.0

        model_info = ModelInfo(
            name="unified-intel-engine-demo",
            version="0.2.0",
            latency_ms=latency_ms,
        )

        metadata = {
            **req.metadata,
            "normalized_language": lang,
            "source": req.source,
            "domain": req.domain,
        }

        # add sentiment provider info into metadata as well
        try:
            metadata["sentiment_source"] = getattr(sentiment, "source", "unknown")
        except Exception:
            metadata["sentiment_source"] = "unknown"
        metadata["gemini_fallback"] = gemini_fallback

        return AnalyzeResponse(
            sentiment=sentiment,
            emotion=emotion,
            toxicity=toxicity,
            intent=intent,
            topic=topic,
            incident=incident,
            ner=ner,
            locations=locations,
            summary=summary,
            aspect_sentiment=aspect_sent,
            similarity=similarity,
            embedding=embedding,
            spam=spam,
            quality=quality,
            explainability=explain,
            confidence=confidence,
            action=action,
            metadata=metadata,
            model_info=model_info,
        )
