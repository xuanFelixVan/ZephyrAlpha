# [A_module] module_id=MOD-SHR_capacity_digital_twin | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TwinState:
    cpu_utilization: float
    memory_utilization: float
    io_throughput: float
    active_connections: int
    timestamp: str


class CapacityDigitalTwin:
    def __init__(self, name: str) -> None:
        self._name = name
        self._states: list[TwinState] = []
        self._max_states = 1000

    def ingest(self, state: TwinState) -> None:
        self._states.append(state)
        if len(self._states) > self._max_states:
            self._states = self._states[-self._max_states:]

    def predict(self, horizon_steps: int = 10) -> TwinState:
        if not self._states:
            return TwinState(0.0, 0.0, 0.0, 0, "")
        last = self._states[-1]
        return TwinState(
            last.cpu_utilization,
            last.memory_utilization,
            last.io_throughput,
            last.active_connections,
            datetime.now(timezone.utc).isoformat(),
        )

    @property
    def name(self) -> str:
        return self._name
