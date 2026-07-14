from __future__ import annotations

from typing import Any, Callable


class AgentRegistry:
    """Registry for pluggable investigation agents."""

    def __init__(self) -> None:
        self._agents: dict[str, Callable[[], Any]] = {}

    def register(self, name: str, factory: Callable[[], Any]) -> None:
        self._agents[name] = factory

    def create(self, name: str) -> Any:
        factory = self._agents.get(name)
        if factory is None:
            raise KeyError(f"No agent registered for {name}")
        return factory()

    def names(self) -> list[str]:
        return sorted(self._agents.keys())
