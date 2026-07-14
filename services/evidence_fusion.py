from __future__ import annotations

from typing import Any


class EvidenceFusionEngine:
    """Fuse structured findings into hypothesis-level evidence scores."""

    def __init__(self, contradiction_penalty: float = 0.12) -> None:
        self.contradiction_penalty = contradiction_penalty

    def fuse(self, findings: list[dict[str, Any]], ml_probability: float) -> dict[str, Any]:
        hypothesis_scores: dict[str, float] = {}
        hypothesis_support: dict[str, list[dict[str, Any]]] = {}

        for finding in findings:
            hypothesis = finding.get("fraud_hypothesis", "misc")
            confidence = float(finding.get("confidence", 0.0) or 0.0)
            severity = self._severity_weight(finding.get("severity", "low"))
            business_impact = float(finding.get("business_impact", 0.0) or 0.0)
            evidence_quality = float(finding.get("evidence_quality", 0.0) or 0.0)
            score = confidence * 0.5 + severity * 0.25 + business_impact * 0.15 + evidence_quality * 0.1
            hypothesis_scores[hypothesis] = hypothesis_scores.get(hypothesis, 0.0) + score
            hypothesis_support.setdefault(hypothesis, []).append(finding)

        ranked_hypotheses = sorted(
            hypothesis_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        top_hypothesis, top_score = ranked_hypotheses[0] if ranked_hypotheses else ("none", 0.0)
        contradiction = max(0.0, len(ranked_hypotheses) - 1) * self.contradiction_penalty
        final_score = round(min(0.99, (0.6 * top_score) + (0.4 * ml_probability) - contradiction), 3)

        return {
            "hypotheses": [
                {
                    "hypothesis": hypothesis,
                    "score": round(score, 3),
                    "supporting_findings": len(hypothesis_support.get(hypothesis, [])),
                }
                for hypothesis, score in ranked_hypotheses
            ],
            "top_hypothesis": top_hypothesis,
            "top_hypothesis_score": round(top_score, 3),
            "final_score": final_score,
        }

    def _severity_weight(self, severity: str) -> float:
        weights = {"low": 0.3, "medium": 0.6, "high": 0.9, "critical": 1.0}
        return weights.get(str(severity).lower(), 0.3)
