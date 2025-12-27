import time
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ModelInfo,
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


class UnifiedEngine:
    """Single engine instance apps can import (Feature 19 & 21)."""

    def __init__(self):
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

    def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        start = time.time()
        text_norm, lang = preprocess(req.text, req.language)

        sentiment = self.sentiment.analyze(text_norm, lang)
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
        quality = self.quality.score(text_norm)
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
            version="0.1.0",
            latency_ms=latency_ms,
        )

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
            metadata={
                **req.metadata,
                "normalized_language": lang,
                "source": req.source,
                "domain": req.domain,
            },
            model_info=model_info,
        )
