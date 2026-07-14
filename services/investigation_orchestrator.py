from __future__ import annotations

from typing import Any


class InvestigationOrchestrator:
    """Simple orchestration layer for follow-up investigation triggers."""

    def __init__(self) -> None:
        self._agent_registry = {
            "provider": "provider",
            "claim": "claim",
            "beneficiary": "beneficiary",
            "temporal": "temporal",
        }

    def build_follow_up_steps(self, coordinator_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert collaboration triggers into actionable follow-up steps."""
        steps: list[dict[str, Any]] = []
        for trigger in coordinator_payload.get("collaboration_triggers", []):
            target = trigger.get("target_agent")
            if target not in self._agent_registry:
                continue
            steps.append(
                {
                    "target_agent": target,
                    "reason": trigger.get("reason", "Follow-up investigation"),
                    "source_agent": trigger.get("source_agent"),
                    "confidence": trigger.get("confidence", 0.0),
                    "status": "queued",
                }
            )
        return steps
