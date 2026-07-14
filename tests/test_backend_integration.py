import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app


class BackendIntegrationTests(unittest.TestCase):
    def test_investigation_endpoint_returns_report(self) -> None:
        client = TestClient(app)
        response = client.post("/investigate", json={"provider_id": "PRV51001"})
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["Provider"], "PRV51001")
        self.assertIn("investigation_summary", payload)
        self.assertIn("coordinator", payload["investigation_summary"])
        self.assertIn("reusable_agent_findings", payload)
