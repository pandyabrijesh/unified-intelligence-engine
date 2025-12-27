from ..schemas import (
    ActionResult,
    SentimentResult,
    IncidentResult,
    ToxicityResult,
    IntentResult,
    SpamResult,
    QualityResult,
)


class ActionRecommender:
    def recommend(
        self,
        sentiment: SentimentResult,
        incident: IncidentResult,
        toxicity: ToxicityResult,
        intent: IntentResult,
        spam: SpamResult,
        quality: QualityResult,
        domain: str,
        source: str,
    ) -> ActionResult:
        if spam.is_spam:
            return ActionResult(
                recommended_action="ignore_or_mark_spam",
                priority="low",
                notes="Classified as spam; filter from dashboards.",
            )

        if incident.is_incident and incident.severity in {"high", "medium"}:
            return ActionResult(
                recommended_action="escalate_to_control_room",
                priority="high",
                notes=f"Incident={incident.category}, severity={incident.severity}.",
            )

        if domain == "product" and sentiment.label.startswith("negative"):
            return ActionResult(
                recommended_action="create_support_ticket",
                priority="medium",
                notes="Negative product feedback; route to service team.",
            )

        if toxicity.is_toxic:
            return ActionResult(
                recommended_action="send_to_moderation_queue",
                priority="medium",
                notes="Toxic language; manual review advised.",
            )

        if sentiment.label.startswith("positive"):
            return ActionResult(
                recommended_action="log_positive_feedback",
                priority="low",
                notes="Positive feedback; useful for reports or testimonials.",
            )

        return ActionResult(
            recommended_action="log_for_analytics",
            priority="low",
            notes="No critical signal; keep for analytics and trend analysis.",
        )
