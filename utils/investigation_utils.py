from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

Direction = Literal["high", "low"]

DEFAULT_HIGH_PERCENTILE = 0.95
DEFAULT_LOW_PERCENTILE = 0.05
DEFAULT_ZSCORE_THRESHOLD = 2.0

REQUIRED_REPORT_FIELDS = {"Provider", "fraud_probability", "investigation_summary", "tasks"}
REQUIRED_COORDINATOR_FIELDS = {
    "Fraud Score",
    "Provider Risk",
    "Claim Risk",
    "Beneficiary Risk",
    "Evidence",
    "Recommendation",
    "Priority",
    "Confidence",
}
REQUIRED_PROVIDER_DF_COLUMNS = {"Provider", "TotalClaims", "UniquePatients", "InpatientRatio"}
REQUIRED_PROBABILITY_COLUMNS = {"Provider", "fraud_probability"}


def create_probability_frame(
    provider_df: pd.DataFrame,
    probabilities: list[float],
    provider_column: str = "Provider",
) -> pd.DataFrame:
    """Build a provider-level fraud probability frame from model outputs."""
    return pd.DataFrame({
        provider_column: provider_df[provider_column].astype(str),
        "fraud_probability": probabilities,
    })


def load_investigation_reports(output_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Load the combined investigation report bundle from disk."""
    output_dir = Path(output_dir or "outputs")
    report_path = output_dir / "investigation_reports.json"
    if not report_path.exists():
        return []
    with report_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_column_reference_stats(
    provider_df: pd.DataFrame,
    column: str,
    provider_column: str = "Provider",
) -> dict[str, Any] | None:
    """Compute population reference statistics for a single provider-level metric."""
    if column not in provider_df.columns:
        return None

    values = pd.to_numeric(provider_df[column], errors="coerce")
    valid_mask = values.notna()
    if not valid_mask.any():
        return None

    valid_values = values[valid_mask]
    rank_percentiles = valid_values.rank(method="average", pct=True)
    mean_val = float(valid_values.mean())
    std_val = float(valid_values.std(ddof=0)) if len(valid_values) > 1 else 0.0
    p95 = float(np.percentile(valid_values, 95))
    p05 = float(np.percentile(valid_values, 5))
    mean_plus_2std = mean_val + (2.0 * std_val)

    by_provider = {
        str(provider_id): float(percentile)
        for provider_id, percentile in zip(
            provider_df.loc[valid_mask, provider_column].astype(str),
            rank_percentiles,
        )
    }

    return {
        "median": float(valid_values.median()),
        "mean": mean_val,
        "std": std_val,
        "p95": p95,
        "p05": p05,
        "mean_plus_2std": mean_plus_2std,
        "by_provider": by_provider,
    }


def build_reference_stats(
    provider_df: pd.DataFrame,
    columns: list[str],
    provider_column: str = "Provider",
) -> dict[str, dict[str, Any]]:
    """Build reference statistics for all requested provider-level metrics."""
    reference_stats: dict[str, dict[str, Any]] = {}
    for column in columns:
        stats = compute_column_reference_stats(provider_df, column, provider_column)
        if stats is not None:
            reference_stats[column] = stats
    return reference_stats


def compute_row_zscore(value: float, mean_val: float, std_val: float) -> float:
    """Compute a z-score for a provider metric relative to the peer population."""
    if std_val <= 0:
        return 0.0
    return (value - mean_val) / std_val


def resolve_row_reference_stats(
    provider_row: dict[str, Any],
    reference_stats: dict[str, dict[str, Any]],
    provider_column: str = "Provider",
) -> dict[str, dict[str, float]]:
    """Attach provider-specific percentile and z-score values to reference stats."""
    provider_id = str(provider_row.get(provider_column, ""))
    row_reference_stats: dict[str, dict[str, float]] = {}

    for metric, stats in reference_stats.items():
        raw_value = provider_row.get(metric)
        if raw_value is None or not isinstance(raw_value, (int, float, np.floating)):
            continue

        value = float(raw_value)
        mean_val = float(stats.get("mean", 0.0))
        std_val = float(stats.get("std", 0.0))
        percentile = float(stats.get("by_provider", {}).get(provider_id, 0.5))
        zscore = compute_row_zscore(value, mean_val, std_val)

        row_reference_stats[metric] = {
            **stats,
            "percentile": percentile,
            "zscore": zscore,
        }

    return row_reference_stats


def is_metric_elevated(
    value: float,
    stats: dict[str, Any],
    direction: Direction = "high",
    high_percentile: float = DEFAULT_HIGH_PERCENTILE,
    low_percentile: float = DEFAULT_LOW_PERCENTILE,
    zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD,
) -> str | None:
    """
    Flag a metric as elevated or outlier_low using dynamic peer thresholds.

    High-risk metrics trigger when value exceeds the 95th percentile, mean + 2*std,
    or z-score >= 2. Low-risk metrics trigger on the inverse thresholds.
    """
    percentile = float(stats.get("percentile", 0.5))
    zscore = float(stats.get("zscore", 0.0))
    std_val = float(stats.get("std", 0.0))
    mean_plus_2std = float(stats.get("mean_plus_2std", stats.get("mean", 0.0)))
    p05 = float(stats.get("p05", 0.0))

    if direction == "high":
        exceeds_dynamic_mean = std_val > 0 and value >= mean_plus_2std
        if percentile >= high_percentile or zscore >= zscore_threshold or exceeds_dynamic_mean:
            return "elevated"
        return None

    below_dynamic_mean = std_val > 0 and value <= p05
    if percentile <= low_percentile or zscore <= -zscore_threshold or below_dynamic_mean:
        return "outlier_low"
    return None


def build_evidence_item(
    metric: str,
    value: float,
    stats: dict[str, Any],
    signal: str,
) -> dict[str, Any]:
    """Create a structured evidence record for a flagged metric."""
    return {
        "metric": metric,
        "value": round(float(value), 4),
        "percentile": round(float(stats.get("percentile", 0.5)), 3),
        "zscore": round(float(stats.get("zscore", 0.0)), 3),
        "peer_mean": round(float(stats.get("mean", 0.0)), 4),
        "peer_std": round(float(stats.get("std", 0.0)), 4),
        "signal": signal,
    }


def score_from_evidence(
    evidence: list[dict[str, Any]],
    base_score: float,
    evidence_weight: float,
    elevated_weight: float = 0.0,
) -> float:
    """Compute a bounded risk score from the number and severity of evidence items."""
    elevated_count = sum(1 for item in evidence if item.get("signal") == "elevated")
    score = base_score + (evidence_weight * len(evidence)) + (elevated_weight * elevated_count)
    return round(min(1.0, score), 3)


def validate_provider_inputs(
    provider_df: pd.DataFrame,
    fraud_probabilities: pd.DataFrame,
) -> None:
    """Validate required columns exist before running the investigation pipeline."""
    if provider_df.empty:
        raise ValueError("provider_df is empty; no providers available for investigation")

    missing_provider_cols = REQUIRED_PROVIDER_DF_COLUMNS - set(provider_df.columns)
    if missing_provider_cols:
        raise ValueError(
            f"provider_df is missing required columns: {sorted(missing_provider_cols)}"
        )

    if fraud_probabilities.empty:
        raise ValueError("fraud_probabilities is empty; fraud scores are required")

    missing_probability_cols = REQUIRED_PROBABILITY_COLUMNS - set(fraud_probabilities.columns)
    if missing_probability_cols:
        raise ValueError(
            f"fraud_probabilities is missing required columns: {sorted(missing_probability_cols)}"
        )


def validate_investigation_report(report: dict[str, Any]) -> None:
    """
    Validate that a report matches the expected investigation schema.

    Raises ValueError when required fields are missing or malformed.
    """
    missing_top_level = REQUIRED_REPORT_FIELDS - set(report.keys())
    if missing_top_level:
        raise ValueError(f"Report missing top-level fields: {sorted(missing_top_level)}")

    summary = report.get("investigation_summary")
    if not isinstance(summary, dict):
        raise ValueError("investigation_summary must be a dictionary")

    coordinator = summary.get("coordinator")
    if not isinstance(coordinator, dict):
        raise ValueError("investigation_summary.coordinator must be a dictionary")

    missing_coordinator = REQUIRED_COORDINATOR_FIELDS - set(coordinator.keys())
    if missing_coordinator:
        raise ValueError(
            f"Coordinator report missing required fields: {sorted(missing_coordinator)}"
        )

    evidence = coordinator.get("Evidence")
    if not isinstance(evidence, list):
        raise ValueError("Evidence must be a list (use [] when no evidence is found)")

    recommendation = coordinator.get("Recommendation")
    if not isinstance(recommendation, list):
        raise ValueError("Recommendation must be a list")


def extract_coordinator_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Return the coordinator findings as a flat dictionary for downstream consumers."""
    validate_investigation_report(report)
    coordinator = report["investigation_summary"]["coordinator"]
    return {
        "Provider": report["Provider"],
        "Fraud Score": coordinator["Fraud Score"],
        "Provider Risk": coordinator["Provider Risk"],
        "Claim Risk": coordinator["Claim Risk"],
        "Beneficiary Risk": coordinator["Beneficiary Risk"],
        "Evidence": coordinator["Evidence"],
        "Recommendation": coordinator["Recommendation"],
        "Priority": coordinator["Priority"],
        "Confidence": coordinator["Confidence"],
    }


def save_provider_report(report: dict[str, Any], output_dir: str | Path) -> Path:
    """Persist a single provider investigation report as JSON."""
    validate_investigation_report(report)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    provider_id = str(report.get("Provider", "unknown"))
    output_path = output_dir / f"{provider_id}_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Saving report to %s", output_path)
    return output_path


def save_combined_reports(reports: list[dict[str, Any]], output_dir: str | Path) -> Path:
    """Persist the combined investigation report bundle."""
    for report in reports:
        validate_investigation_report(report)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined_path = output_dir / "investigation_reports.json"
    combined_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    logger.info("Saving combined investigation reports to %s", combined_path)
    return combined_path
