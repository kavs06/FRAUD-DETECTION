from __future__ import annotations

from typing import Any

from agents.investigation.base import InvestigationAgent, InvestigationContext


class ClaimInvestigationAgent(InvestigationAgent):
    """Rule-based claim specialist for new investigation architecture."""

    name = "claim"

    def analyze(self, context: InvestigationContext) -> list[dict[str, Any]]:
        provider_row = context.provider_row
        findings: list[dict[str, Any]] = []
        duplicate_ratio = float(provider_row.get("DuplicateClaimsRatio", 0.0) or 0.0)
        if duplicate_ratio > 0.0:
            findings.append(
                {
                    "title": "Claim pattern suggests duplicate or repeated billing",
                    "severity": "high",
                    "confidence": 0.78,
                    "evidence_quality": 0.74,
                    "business_impact": 0.78,
                    "fraud_hypothesis": "duplicate_billing",
                    "evidence": [{"metric": "DuplicateClaimsRatio", "value": duplicate_ratio}],
                    "supporting_metrics": [{"metric": "DuplicateClaimsRatio", "value": duplicate_ratio}],
                    "triggered_checks": ["verify_duplicate_claims"],
                    "recommended_investigation": "Review claim line-level duplication and supporting documentation",
                    "reasoning": "The provider exhibits a duplicate-billing signal based on claim-level metrics.",
                    "agent_name": self.name,
                }
            )
        return findings
