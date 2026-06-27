"""Single-provider reference test for the multi-agent fraud investigation pipeline."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from crews.fraud_investigation_crew import FraudInvestigationCrew
from utils.investigation_utils import (
    extract_coordinator_summary,
    validate_investigation_report,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

THRESHOLD = 0.6
TARGET_PROVIDER = "PRV10019"


def build_synthetic_provider_df(n_providers: int = 20) -> pd.DataFrame:
    """Build a minimal provider feature frame for pipeline testing."""
    rng = np.random.default_rng(42)
    providers = [f"PRV{10000 + i}" for i in range(n_providers)]
    total_claims = rng.integers(50, 500, size=n_providers)
    unique_patients = rng.integers(20, 200, size=n_providers)

    return pd.DataFrame({
        "Provider": providers,
        "TotalReimbursed": rng.uniform(50_000, 500_000, size=n_providers),
        "AvgReimbursed": rng.uniform(500, 5000, size=n_providers),
        "MaxReimbursed": rng.uniform(5_000, 20_000, size=n_providers),
        "TotalClaims": total_claims,
        "InpatientRatio": rng.uniform(0.1, 0.9, size=n_providers),
        "PatientsPerClaim": unique_patients / total_claims,
        "PhysiciansPerClaim": rng.uniform(0.05, 0.5, size=n_providers),
        "SameAttendOperRate": rng.uniform(0.0, 0.3, size=n_providers),
        "DeceasedPatientRate": rng.uniform(0.0, 0.2, size=n_providers),
        "AvgClaimDuration": rng.uniform(1, 30, size=n_providers),
        "MaxClaimDuration": rng.uniform(10, 90, size=n_providers),
        "AvgDaysInHospital": rng.uniform(0, 10, size=n_providers),
        "TotalDaysInHospital": rng.uniform(0, 500, size=n_providers),
        "AvgDeductible": rng.uniform(0, 500, size=n_providers),
        "TotalDeductible": rng.uniform(0, 10_000, size=n_providers),
        "UniquePatients": unique_patients,
        "AvgPatientAge": rng.uniform(55, 85, size=n_providers),
        "AvgChronicConds": rng.uniform(1, 6, size=n_providers),
    })


def build_single_provider_probabilities(provider_df: pd.DataFrame) -> pd.DataFrame:
    """Assign fraud probabilities so only the target provider exceeds the threshold."""
    mask = provider_df["Provider"] == TARGET_PROVIDER
    if mask.sum() != 1:
        raise ValueError(f"Expected exactly one row for provider {TARGET_PROVIDER}")

    probabilities = np.where(mask, 0.88, 0.35)
    return pd.DataFrame({
        "Provider": provider_df["Provider"],
        "fraud_probability": probabilities,
    })


def main() -> None:
    provider_df = build_synthetic_provider_df()
    fraud_probs = build_single_provider_probabilities(provider_df)

    output_dir = ROOT / "outputs"
    crew = FraudInvestigationCrew(output_dir=str(output_dir))
    reports = crew.investigate(provider_df, fraud_probs, threshold=THRESHOLD)

    if len(reports) != 1:
        raise AssertionError(
            f"Expected exactly one investigation report, received {len(reports)}"
        )

    report = reports[0]
    validate_investigation_report(report)
    summary = extract_coordinator_summary(report)

    report_path = output_dir / f"{summary['Provider']}_report.json"
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
