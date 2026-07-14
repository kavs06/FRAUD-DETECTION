import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.report_generation_service import ReportGenerationService


class ReportGenerationServiceTests(unittest.TestCase):
    def test_generates_markdown_and_structured_sections(self) -> None:
        service = ReportGenerationService()
        context = {
            "provider_id": "PRV10019",
            "fraud_prediction": {"label": "Fraud", "probability": 0.94},
            "investigation_findings": [{"source": "provider", "summary": "High reimbursement"}],
            "fraud_hypotheses": [{"hypothesis": "Billing anomaly", "confidence": 0.94}],
            "shap_explanations": [{"feature_name": "total_reimbursement", "shap_value": 0.45}],
            "confidence_scores": {"probability": 0.94},
        }

        report = service.generate_report(context)
        self.assertIn("Fraud Investigation Report", report["markdown_report"])
        self.assertIn("executive_summary", report["structured_report"])
        self.assertIn("shap_explanations", report["structured_report"])

    def test_parse_report_returns_fallback_sections(self) -> None:
        service = ReportGenerationService()
        structured = service.parse_report("Simple report", {"shap_explanations": []})
        self.assertIn("executive_summary", structured)
        self.assertIn("shap_explanations", structured)
