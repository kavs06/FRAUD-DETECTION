import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.investigation_service import InvestigationService


class InvestigationServiceTests(unittest.TestCase):
    def test_investigate_provider_returns_report_for_known_provider(self) -> None:
        service = InvestigationService(output_dir=str(ROOT / "outputs_test"))
        report = service.investigate_provider("PRV51001", threshold=0.0)

        self.assertIsInstance(report, dict)
        self.assertEqual(report["Provider"], "PRV51001")
        self.assertIn("investigation_summary", report)


if __name__ == "__main__":
    unittest.main()
