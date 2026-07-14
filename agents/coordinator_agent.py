from __future__ import annotations

import logging
import os
from typing import Any

from schemas.investigation_schema import Finding
from services.evidence_fusion import EvidenceFusionEngine

logger = logging.getLogger(__name__)


class InvestigationCoordinatorAgent:
    """Combines the specialist findings into an overall investigation report."""

    def __init__(self) -> None:
        self._crew_agent = None
        self.fusion_engine = EvidenceFusionEngine()

    @property
    def agent(self):
        if self._crew_agent is None:
            from crewai import Agent

            google_api_key = os.environ.get("GOOGLE_API_KEY")
            if google_api_key:
                os.environ["GEMINI_API_KEY"] = google_api_key
                llm = "gemini/gemini-1.5-flash"
            else:
                llm = None

            self._crew_agent = Agent(
                role="Investigation Coordinator",
                goal="Combine specialist findings into a structured fraud investigation report",
                backstory=(
                    "You synthesize provider, claim, and beneficiary evidence into a concise investigation package "
                    "that is ready for human review."
                ),
                verbose=False,
                allow_delegation=False,
                llm=llm,
            )
        return self._crew_agent

    def analyze(
        self,
        provider_row: dict[str, Any],
        specialist_findings: list[dict[str, Any]],
        fraud_probability: float,
    ) -> dict[str, Any]:
        """Aggregate specialist outputs into a structured investigation report."""
        provider_risk = 0.0
        claim_risk = 0.0
        beneficiary_risk = 0.0
        evidence: list[dict[str, Any]] = []
        structured_findings: list[dict[str, Any]] = []
        collaboration_triggers: list[dict[str, Any]] = []

        for finding in specialist_findings:
            agent_type = finding.get("agent")
            risk = float(finding.get("risk_score", 0.0))
            if agent_type == "provider":
                provider_risk = risk
            elif agent_type == "claim":
                claim_risk = risk
            elif agent_type == "beneficiary":
                beneficiary_risk = risk

            evidence.extend(finding.get("evidence", []))

            if finding.get("evidence"):
                signal_strength = min(1.0, 0.35 + 0.08 * len(finding.get("evidence", [])) + 0.1 * risk)
                severity = "high" if signal_strength >= 0.75 else "medium" if signal_strength >= 0.5 else "low"
                fraud_hypothesis = self._infer_hypothesis(agent_type, finding.get("evidence", []))
                finding_payload = Finding(
                    title=self._build_title(agent_type, fraud_hypothesis),
                    severity=severity,
                    confidence=round(min(0.99, signal_strength), 3),
                    evidence_quality=round(min(1.0, 0.5 + 0.05 * len(finding.get("evidence", []))), 3),
                    business_impact=round(min(1.0, 0.4 + 0.2 * risk + 0.1 * fraud_probability), 3),
                    fraud_hypothesis=fraud_hypothesis,
                    evidence=finding.get("evidence", []),
                    supporting_metrics=[{"metric": item.get("metric"), "value": item.get("value")} for item in finding.get("evidence", [])],
                    triggered_checks=self._triggered_checks(agent_type, fraud_hypothesis),
                    recommended_investigation=self._recommend_investigation(agent_type, fraud_hypothesis),
                    reasoning=self._build_reasoning(agent_type, fraud_hypothesis, risk),
                    agent_name=agent_type,
                ).to_dict()
                structured_findings.append(finding_payload)
                collaboration_triggers.extend(self._build_collaboration_triggers(agent_type, fraud_hypothesis, finding_payload))

        specialist_avg = (provider_risk + claim_risk + beneficiary_risk) / 3.0
        combined_score = round(min(1.0, (specialist_avg * 0.7) + (fraud_probability * 0.3)), 3)

        if combined_score >= 0.8:
            priority = "High"
            recommendation = [
                "Escalate to manual audit immediately",
                "Suspend payments pending review",
                "Conduct comprehensive beneficiary interview",
                "Verify procedure code accuracy on inpatient billing",
            ]
        elif combined_score >= 0.6:
            priority = "Medium"
            recommendation = [
                "Perform targeted claims review on procedural codes",
                "Monitor claim volumes and patient-mix trends",
                "Request patient record samples for code validation",
            ]
        else:
            priority = "Low"
            recommendation = [
                "Continue baseline monitoring of billing patterns",
                "Re-evaluate during quarterly review cycles",
            ]

        confidence = round(min(0.99, 0.5 + (0.05 * len(evidence)) + (0.2 * fraud_probability)), 3)
        fusion_output = self.fusion_engine.fuse(structured_findings, fraud_probability)
        overall_confidence = round(min(0.99, max(confidence, combined_score, fusion_output["final_score"])), 3)

        logger.debug(
            "Coordinator report for %s: fraud_score=%s priority=%s",
            provider_row.get("Provider"),
            combined_score,
            priority,
        )

        return {
            "Fraud Score": combined_score,
            "Provider Risk": provider_risk,
            "Claim Risk": claim_risk,
            "Beneficiary Risk": beneficiary_risk,
            "Evidence": evidence,
            "Recommendation": recommendation,
            "Priority": priority,
            "Confidence": confidence,
            "risk_score": combined_score,
            "risk_tier": priority.lower(),
            "agent": "coordinator",
            "fraud_probability": round(float(fraud_probability), 3),
            "recommended_actions": recommendation,
            "structured_findings": structured_findings,
            "overall_confidence": overall_confidence,
            "collaboration_triggers": collaboration_triggers,
            "temporal_context": self._build_temporal_context(provider_row),
            "cohort_context": self._build_cohort_context(provider_row),
            "evidence_fusion": fusion_output,
        }

    def _infer_hypothesis(self, agent_type: str, evidence: list[dict[str, Any]]) -> str:
        metrics = {item.get("metric") for item in evidence}
        if agent_type == "claim":
            if "DuplicateClaimsRatio" in metrics or "MaxClaimsSingleDay" in metrics:
                return "duplicate_billing"
            if "TopProcedureCodeRatio" in metrics:
                return "upcoding"
            return "excessive_services"
        if agent_type == "beneficiary":
            if "BeneficiaryConcentration" in metrics or "ProviderDependency" in metrics:
                return "identity_misuse"
            return "referral_abuse"
        if agent_type == "provider":
            if "AvgReimbursed" in metrics or "MaxReimbursed" in metrics:
                return "upcoding"
            return "excessive_services"
        return "excessive_services"

    def _build_title(self, agent_type: str, fraud_hypothesis: str) -> str:
        titles = {
            "provider": "Provider reimbursement pattern deviates from peer norms",
            "claim": "Claim pattern indicates suspicious billing behavior",
            "beneficiary": "Beneficiary utilization pattern indicates concentrated risk",
        }
        return titles.get(agent_type, "Suspicious billing activity identified")

    def _triggered_checks(self, agent_type: str, fraud_hypothesis: str) -> list[str]:
        checks = {
            "provider": [
                "review_provider_fee_schedule",
                "inspect_high_cost_procedure_mix",
                "validate_claim_volume_trends",
            ],
            "claim": [
                "verify_duplicate_claims",
                "review_procedure_code_distribution",
                "check_claim_velocity",
            ],
            "beneficiary": [
                "review_beneficiary_concentration",
                "inspect_provider_dependency",
                "validate_patient_overlap",
            ],
        }
        return checks.get(agent_type, [])

    def _recommend_investigation(self, agent_type: str, fraud_hypothesis: str) -> str:
        if fraud_hypothesis == "duplicate_billing":
            return "Audit all duplicate claims and request supporting documentation for the affected dates"
        if fraud_hypothesis == "upcoding":
            return "Perform medical record review and validate procedure coding against services rendered"
        if fraud_hypothesis == "identity_misuse":
            return "Review beneficiary enrollment and patient overlap data with provider records"
        return "Escalate for targeted review of utilization patterns and billing behavior"

    def _build_reasoning(self, agent_type: str, fraud_hypothesis: str, risk: float) -> str:
        return (
            f"{agent_type.title()} analysis identified a {fraud_hypothesis.replace('_', ' ')} signal with "
            f"risk score {risk:.2f}. The finding is supported by multiple peer-relative indicators and "
            "should be examined with targeted documentation review."
        )

    def _build_collaboration_triggers(
        self,
        agent_type: str,
        fraud_hypothesis: str,
        finding_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        if agent_type == "provider" and fraud_hypothesis == "upcoding":
            return [{
                "source_agent": agent_type,
                "target_agent": "claim",
                "reason": "inspect procedure mix and duplicate billing",
                "confidence": finding_payload.get("confidence", 0.0),
            }]
        if agent_type == "beneficiary" and fraud_hypothesis == "identity_misuse":
            return [{
                "source_agent": agent_type,
                "target_agent": "provider",
                "reason": "review provider concentration and patient overlap",
                "confidence": finding_payload.get("confidence", 0.0),
            }]
        if agent_type == "claim" and fraud_hypothesis == "duplicate_billing":
            return [{
                "source_agent": agent_type,
                "target_agent": "temporal",
                "reason": "evaluate whether duplicate patterns are accelerating over time",
                "confidence": finding_payload.get("confidence", 0.0),
            }]
        return []

    def _build_temporal_context(self, provider_row: dict[str, Any]) -> dict[str, Any]:
        claim_growth = float(provider_row.get("ClaimGrowth", 0.0) or 0.0)
        reimbursement = float(provider_row.get("AvgReimbursed", 0.0) or 0.0)
        return {
            "claim_growth": round(claim_growth, 3),
            "avg_reimbursement": round(reimbursement, 3),
            "temporal_signal": "spike" if claim_growth > 0.2 else "stable",
        }

    def _build_cohort_context(self, provider_row: dict[str, Any]) -> dict[str, Any]:
        specialty = str(provider_row.get("Specialty", "unknown") or "unknown")
        region = str(provider_row.get("Region", "unknown") or "unknown")
        return {
            "specialty": specialty,
            "region": region,
            "cohort_strategy": "compare against same specialty and region peers",
        }
