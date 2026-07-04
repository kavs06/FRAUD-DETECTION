"""Single-provider reference invocation for the shared investigation service."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.investigation_service import InvestigationService
from utils.investigation_utils import extract_coordinator_summary, validate_investigation_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

THRESHOLD = 0.6
TARGET_PROVIDER = "PRV51001"


def main() -> None:
    service = InvestigationService(output_dir=str(ROOT / "outputs"))
    report = service.investigate_provider(TARGET_PROVIDER, threshold=THRESHOLD)

    validate_investigation_report(report)
    summary = extract_coordinator_summary(report)

    report_path = ROOT / "outputs" / f"{summary['Provider']}_report.json"
    if not report_path.exists():
        raise AssertionError(f"Expected report file was not written: {report_path}")

    print(f"Provider ID: {summary['Provider']}")
    print(f"Fraud Score: {summary['Fraud Score']}")
    print(f"Provider Risk: {summary['Provider Risk']}")
    print(f"Claim Risk: {summary['Claim Risk']}")
    print(f"Beneficiary Risk: {summary['Beneficiary Risk']}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
