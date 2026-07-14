from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationContext:
    """Shared context object passed between investigation agents."""

    provider_id: str
    provider_row: dict[str, Any]
    cohort_context: dict[str, Any] = field(default_factory=dict)
    temporal_context: dict[str, Any] = field(default_factory=dict)
    ml_probability: float = 0.0
    findings: list[dict[str, Any]] = field(default_factory=list)
    collaboration_triggers: list[dict[str, Any]] = field(default_factory=list)


class InvestigationAgent(ABC):
    """Base class for all domain-specialist investigation agents."""

    name: str = "investigation_agent"

    @abstractmethod
    def analyze(self, context: InvestigationContext) -> list[dict[str, Any]]:
        """Produce structured findings for the provided investigation context."""
        raise NotImplementedError
