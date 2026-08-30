# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.heartbeat_server
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: timeout_seconds 参数
#   fields: 参数 timeout_seconds（无注解）
#   code: heartbeat_server.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HeartbeatServer
#   name_en: HeartbeatServer
#   intro: class HeartbeatServer 源码 L63-L80
#   desc: 公共方法（定义序）: register, beat, check, check_all；源码 L63-L80
#   inputs: timeout_seconds
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: HeartbeatServer
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
