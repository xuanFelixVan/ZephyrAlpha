# [A_module] module_id=MOD-SHR_heartbeat_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class HeartbeatStatus:
    component_id: str
    last_heartbeat: float
    interval_seconds: float
    is_alive: bool


class HeartbeatServer:
    def __init__(self, timeout_seconds: float = 30.0):
        self._timeout = timeout_seconds
        self._heartbeats: dict[str, float] = {}

    def register(self, component_id: str) -> None:
        self._heartbeats[component_id] = time.time()

    def beat(self, component_id: str) -> None:
        self._heartbeats[component_id] = time.time()

    def check(self, component_id: str) -> HeartbeatStatus:
        last = self._heartbeats.get(component_id, 0.0)
        elapsed = time.time() - last
        return HeartbeatStatus(component_id, last, self._timeout, elapsed <= self._timeout)

    def check_all(self) -> list[HeartbeatStatus]:
        return [self.check(cid) for cid in self._heartbeats]
