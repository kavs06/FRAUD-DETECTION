from __future__ import annotations

from typing import Any

from agents.investigation.base import InvestigationAgent, InvestigationContext


class BeneficiaryInvestigationAgent(InvestigationAgent):
    """Rule-based beneficiary specialist for new investigation architecture."""

    name = "beneficiary"

    def analyze(self, context: InvestigationContext) -> list[dict[str, Any]]:
        provider_row = context.provider_row
        findings: list[dict[str, Any]] = []
        concentration = float(provider_row.get("BeneficiaryConcentration", 0.0) or 0.0)
        if concentration > 0.0:
            findings.append(
                {
                    "title": "Beneficiary concentration suggests possible identity misuse",
                    "severity": "medium",
                    "confidence": 0.7,
                    "evidence_quality": 0.69,
                    "business_impact": 0.72,
                    "fraud_hypothesis": "identity_misuse",
                    "evidence": [{"metric": "BeneficiaryConcentration", "value": concentration}],
                    "supporting_metrics": [{"metric": "BeneficiaryConcentration", "value": concentration}],
                    "triggered_checks": ["review_beneficiary_concentration"],
                    "recommended_investigation": "Examine beneficiary overlap and enrollment history",
                    "reasoning": "Beneficiary concentration is elevated and warrants direct review.",
                    "agent_name": self.name,
                }
            )
        return findings
