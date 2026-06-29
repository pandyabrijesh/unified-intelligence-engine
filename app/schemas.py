from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Standard request for all apps (Feature 2)."""
    text: str = Field(..., min_length=1)
    language: str = Field("auto")
    source: str = Field("generic")
    domain: str = Field("generic")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SentimentResult(BaseModel):
    label: str
    score: float
    raw_label: Optional[str] = None
    source: Optional[str] = None


class EmotionResult(BaseModel):
    label: str
    scores: Dict[str, float]


class ToxicityResult(BaseModel):
    is_toxic: bool
    score: float


class IntentResult(BaseModel):
    label: str
    scores: Dict[str, float]


class TopicResult(BaseModel):
    label: str
    scores: Dict[str, float]


class IncidentResult(BaseModel):
    is_incident: bool
    category: Optional[str] = None
    severity: Optional[str] = None


class NERResult(BaseModel):
    entities: Dict[str, str]


class LocationResult(BaseModel):
    locations: Dict[str, Dict[str, float]]


class SummaryResult(BaseModel):
    short: str
    long: str


class AspectSentimentResult(BaseModel):
    aspects: Dict[str, str]


class SimilarityResult(BaseModel):
    reference_id: Optional[str] = None
    similarity: float = 0.0


class EmbeddingResult(BaseModel):
    vector: List[float]


class SpamResult(BaseModel):
    is_spam: bool
    reasons: List[str]


class QualityResult(BaseModel):
    score: float
    issues: List[str]


class ExplainabilityResult(BaseModel):
    positive_terms: List[str]
    negative_terms: List[str]
    rationale: str


class ConfidenceResult(BaseModel):
    score: float
    reasons: List[str]


class ActionResult(BaseModel):
    recommended_action: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None


class ModelInfo(BaseModel):
    name: str
    version: str
    latency_ms: float


class AnalyzeResponse(BaseModel):
    """Full response with all bundled outputs."""
    sentiment: SentimentResult
    emotion: EmotionResult
    toxicity: ToxicityResult
    intent: IntentResult
    topic: TopicResult
    incident: IncidentResult
    ner: NERResult
    locations: LocationResult
    summary: SummaryResult
    aspect_sentiment: AspectSentimentResult
    similarity: SimilarityResult
    embedding: EmbeddingResult
    spam: SpamResult
    quality: QualityResult
    explainability: ExplainabilityResult
    confidence: ConfidenceResult
    action: ActionResult
    metadata: Dict[str, Any]
    model_info: ModelInfo


class BatchAnalyzeRequest(BaseModel):
    items: List[AnalyzeRequest]


class BatchAnalyzeResponse(BaseModel):
    items: List[AnalyzeResponse]