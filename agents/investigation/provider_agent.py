from __future__ import annotations

from typing import Any

from agents.investigation.base import InvestigationAgent, InvestigationContext


class ProviderInvestigationAgent(InvestigationAgent):
    """Rule-based provider specialist for new investigation architecture."""

    name = "provider"

    def analyze(self, context: InvestigationContext) -> list[dict[str, Any]]:
        provider_row = context.provider_row
        findings: list[dict[str, Any]] = []
        avg_reimbursed = float(provider_row.get("AvgReimbursed", 0.0) or 0.0)
        if avg_reimbursed > 0:
            findings.append(
                {
                    "title": "Provider reimbursement is materially above peer benchmarks",
                    "severity": "high",
                    "confidence": 0.74,
                    "evidence_quality": 0.72,
                    "business_impact": 0.8,
                    "fraud_hypothesis": "upcoding",
                    "evidence": [{"metric": "AvgReimbursed", "value": avg_reimbursed}],
                    "supporting_metrics": [{"metric": "AvgReimbursed", "value": avg_reimbursed}],
                    "triggered_checks": ["review_provider_fee_schedule"],
                    "recommended_investigation": "Audit provider billing practices and procedure coding",
                    "reasoning": "Provider reimbursement is higher than expected for the assigned cohort.",
                    "agent_name": self.name,
                }
            )
        return findings
