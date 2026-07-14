from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    """Structured investigation finding produced by a specialist agent."""

    title: str
    severity: str
    confidence: float
    evidence_quality: float
    business_impact: float
    fraud_hypothesis: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    supporting_metrics: list[dict[str, Any]] = field(default_factory=list)
    triggered_checks: list[str] = field(default_factory=list)
    recommended_investigation: str = ""
    reasoning: str = ""
    agent_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "confidence": round(self.confidence, 3),
            "evidence_quality": round(self.evidence_quality, 3),
            "business_impact": round(self.business_impact, 3),
            "fraud_hypothesis": self.fraud_hypothesis,
            "evidence": self.evidence,
            "supporting_metrics": self.supporting_metrics,
            "triggered_checks": self.triggered_checks,
            "recommended_investigation": self.recommended_investigation,
            "reasoning": self.reasoning,
            "agent_name": self.agent_name,
        }


@dataclass
class InvestigationCase:
    """Aggregated investigation result for a provider."""

    provider_id: str
    ml_probability: float
    findings: list[Finding] = field(default_factory=list)
    overall_confidence: float = 0.0
    priority: str = "low"
    recommended_next_actions: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "ml_probability": round(self.ml_probability, 3),
            "findings": [finding.to_dict() for finding in self.findings],
            "overall_confidence": round(self.overall_confidence, 3),
            "priority": self.priority,
            "recommended_next_actions": self.recommended_next_actions,
            "summary": self.summary,
        }
