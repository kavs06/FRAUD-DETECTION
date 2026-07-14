from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """Reusable service for turning model explanations into structured payloads."""

    def __init__(self) -> None:
        self._logger = logger

    def build_explanation_payload(
        self,
        *,
        provider_id: str,
        prediction: str,
        probability: float,
        feature_contributions: list[dict[str, Any]],
        explanation_text: str,
        plot_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a structured explanation payload for downstream consumers."""

        ranked_features = []
        for index, item in enumerate(feature_contributions, start=1):
            shap_value = float(item.get("shap_value", 0.0))
            contribution_direction = "positive" if shap_value >= 0 else "negative"
            ranked_features.append(
                {
                    "feature_name": item.get("feature_name") or item.get("feature") or "unknown",
                    "shap_value": shap_value,
                    "feature_value": item.get("feature_value"),
                    "baseline_value": item.get("baseline_value"),
                    "contribution_direction": contribution_direction,
                    "importance_rank": index,
                }
            )

        ranked_features.sort(key=lambda entry: abs(entry["shap_value"]), reverse=True)
        for index, entry in enumerate(ranked_features, start=1):
            entry["importance_rank"] = index

        return {
            "provider_id": provider_id,
            "prediction": prediction,
            "probability": round(float(probability), 4),
            "structured_explanation": {
                "summary": explanation_text,
                "features": ranked_features,
                "plot_config": plot_config or {},
            },
            "plots": {},
        }

    def build_plot_payload(self, *, explanation_payload: dict[str, Any]) -> dict[str, Any]:
        """Keep plot generation optional and separate from the structured payload."""
        return {
            "summary_plot": None,
            "waterfall_plot": None,
            "source": explanation_payload,
        }
