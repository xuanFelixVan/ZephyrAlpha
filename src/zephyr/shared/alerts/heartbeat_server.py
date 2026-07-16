# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.alerts.heartbeat_server
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
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
