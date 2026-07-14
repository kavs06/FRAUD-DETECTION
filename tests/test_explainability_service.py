import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app
from services.explainability_service import ExplainabilityService


class ExplainabilityServiceTests(unittest.TestCase):
    def test_structured_explanation_includes_ranked_features(self) -> None:
        service = ExplainabilityService()
        payload = service.build_explanation_payload(
            provider_id="PRV10019",
            prediction="Fraud",
            probability=0.94,
            feature_contributions=[
                {
                    "feature_name": "num_inpatient_claims",
                    "shap_value": 0.45,
                    "feature_value": 12,
                    "baseline_value": 0.0,
                },
                {
                    "feature_name": "total_reimbursement",
                    "shap_value": 0.30,
                    "feature_value": 14200,
                    "baseline_value": 0.0,
                },
            ],
            explanation_text="Example explanation",
        )

        self.assertEqual(payload["provider_id"], "PRV10019")
        features = payload["structured_explanation"]["features"]
        self.assertEqual(features[0]["feature_name"], "num_inpatient_claims")
        self.assertEqual(features[0]["importance_rank"], 1)
        self.assertEqual(features[0]["contribution_direction"], "positive")
        self.assertEqual(features[1]["importance_rank"], 2)
        self.assertIn("feature_name", features[0])

    def test_explain_endpoint_returns_structured_explanation(self) -> None:
        client = TestClient(app)
        response = client.get("/explain/PRV51001")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("structured_explanation", payload)
        self.assertIn("features", payload["structured_explanation"])
        self.assertGreaterEqual(len(payload["structured_explanation"]["features"]), 1)
        first_feature = payload["structured_explanation"]["features"][0]
        self.assertIn("feature_name", first_feature)
        self.assertIn("shap_value", first_feature)
        self.assertIn("contribution_direction", first_feature)
