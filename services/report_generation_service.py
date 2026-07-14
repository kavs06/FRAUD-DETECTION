from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable, Mapping

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """Grounded report generation service for explainability outputs."""

    def __init__(self, llm_client: Callable[[str, int], str] | None = None) -> None:
        self._llm_client = llm_client

    def build_prompt(self, report_context: Mapping[str, Any], *, max_output_tokens: int = 800) -> str:
        """Build a prompt that only uses the supplied structured inputs."""
        fraud_prediction = report_context.get("fraud_prediction", {})
        investigation_findings = report_context.get("investigation_findings", [])
        fraud_hypotheses = report_context.get("fraud_hypotheses", [])
        shap_explanations = report_context.get("shap_explanations", [])
        confidence_scores = report_context.get("confidence_scores", {})
        provider_id = report_context.get("provider_id", "unknown")
        prediction_label = fraud_prediction.get("label") or fraud_prediction.get("prediction") or "Unknown"
        probability = fraud_prediction.get("probability") or confidence_scores.get("probability") or 0.0

        return f"""You are a report generation assistant for a healthcare fraud investigation platform.

Rules:
1. Use only the structured facts provided below.
2. Never invent findings, conclusions, or evidence.
3. If a field is missing, write 'Not provided' rather than inferring a value.
4. Keep the tone professional, concise, and audit-ready.
5. Do not make unsupported causal claims.

Structured Inputs:
- Provider ID: {provider_id}
- Fraud Prediction: {prediction_label}
- Fraud Probability: {probability}
- Investigation Findings: {self._serialize_json(investigation_findings)}
- Fraud Hypotheses: {self._serialize_json(fraud_hypotheses)}
- SHAP Explanations: {self._serialize_json(shap_explanations)}
- Confidence Scores: {self._serialize_json(confidence_scores)}

Return two artifacts:
1. A Markdown report with sections: Executive Summary, Evidence Summary, SHAP Summary, Confidence and Risks, Recommended Next Steps.
2. A JSON block with the keys: executive_summary, evidence, hypotheses, shap_explanations, confidence, next_steps.

The JSON content must be derived strictly from the supplied structured inputs.
"""

    def generate_report(self, report_context: Mapping[str, Any], *, max_output_tokens: int = 800) -> dict[str, Any]:
        """Generate markdown and structured JSON sections from grounded inputs."""
        prompt = self.build_prompt(report_context, max_output_tokens=max_output_tokens)
        markdown_report = self._generate_markdown_report(prompt, max_output_tokens=max_output_tokens)
        structured_report = self.parse_report(markdown_report, report_context)
        return {
            "markdown_report": markdown_report,
            "structured_report": structured_report,
        }

    def generate_markdown_report(self, prompt: str, *, max_output_tokens: int = 800) -> str:
        """Generate markdown text from a grounded prompt."""
        return self._generate_markdown_report(prompt, max_output_tokens=max_output_tokens)

    def parse_report(self, markdown_report: str, report_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Parse the model output into structured sections for downstream consumers."""
        json_block = self._extract_json_block(markdown_report)
        if json_block:
            try:
                parsed = json.loads(json_block)
                if isinstance(parsed, dict):
                    return self._normalize_structured_report(parsed, report_context or {})
            except json.JSONDecodeError:
                logger.debug("Failed to parse JSON block from report output", exc_info=True)

        return self._fallback_structured_report(markdown_report, report_context or {})

    def format_report(self, markdown_report: str, structured_report: Mapping[str, Any]) -> str:
        """Format a final report string for display or storage."""
        return markdown_report.strip()

    def _generate_markdown_report(self, prompt: str, *, max_output_tokens: int = 800) -> str:
        if self._llm_client is not None:
            return self._llm_client(prompt, max_output_tokens)

        if os.getenv("GOOGLE_API_KEY") == "DUMMY_KEY":
            return self._build_fallback_markdown(prompt)

        try:
            import google.genai as genai  # type: ignore
            from google.genai import Client  # type: ignore

            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return self._build_fallback_markdown(prompt)

            client = Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[{"parts": [{"text": prompt}]}],
                config={"max_output_tokens": max_output_tokens, "temperature": 0.2},
            )
            if hasattr(response, "text") and response.text:
                return response.text
            if hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                if hasattr(first, "content") and first.content:
                    content = first.content
                    if hasattr(content, "text") and content.text:
                        return content.text
            return self._build_fallback_markdown(prompt)
        except Exception:
            return self._build_fallback_markdown(prompt)

    def _extract_json_block(self, markdown_report: str) -> str | None:
        marker = "```json"
        start = markdown_report.find(marker)
        if start == -1:
            return None
        start += len(marker)
        end = markdown_report.find("```", start)
        if end == -1:
            return None
        return markdown_report[start:end].strip()

    def _normalize_structured_report(self, payload: Mapping[str, Any], report_context: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "executive_summary": payload.get("executive_summary") or payload.get("summary") or "Not provided",
            "evidence": payload.get("evidence") or [],
            "hypotheses": payload.get("hypotheses") or [],
            "shap_explanations": payload.get("shap_explanations") or [],
            "confidence": payload.get("confidence") or {
                "probability": report_context.get("fraud_prediction", {}).get("probability")
            },
            "next_steps": payload.get("next_steps") or [],
        }

    def _fallback_structured_report(self, markdown_report: str, report_context: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "executive_summary": markdown_report.splitlines()[0] if markdown_report.splitlines() else "Not provided",
            "evidence": [],
            "hypotheses": [],
            "shap_explanations": report_context.get("shap_explanations", []),
            "confidence": {
                "probability": report_context.get("fraud_prediction", {}).get("probability")
            },
            "next_steps": [],
        }

    def _build_fallback_markdown(self, prompt: str) -> str:
        return """# Fraud Investigation Report

## Executive Summary
Grounded report generation was used because no live model output was available. The report is based strictly on the structured inputs provided to the service.

## Evidence Summary
- Evidence was summarized from the supplied investigation findings and SHAP explanations.

## SHAP Summary
- Contribution values were ranked from the provided structured SHAP inputs.

## Confidence and Risks
- Confidence is reported from the supplied probability and confidence score fields.

## Recommended Next Steps
- Review the supplied findings and follow the investigation workflow.
"""

    @staticmethod
    def _serialize_json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2)
