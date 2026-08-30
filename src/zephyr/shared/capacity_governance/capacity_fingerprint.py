# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.capacity_fingerprint
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
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
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capacity_fingerprint.py
# 层: 算法
# - id: A1
#   name_zh: ① CapacityFingerprint
#   name_en: CapacityFingerprint
#   intro: class CapacityFingerprint 源码 L63-L82
#   desc: 公共方法（定义序）: capture, compare, get_baseline；源码 L63-L82
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CapacityFingerprint
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapacitySnapshot:
    cpu_pct: float
    mem_pct: float
    disk_pct: float
    net_mbps: float
    active_tasks: int
    timestamp: str


class CapacityFingerprint:
    def __init__(self) -> None:
        self._snapshots: dict[str, CapacitySnapshot] = {}

    def capture(self, component_id: str, snapshot: CapacitySnapshot) -> str:
        self._snapshots[component_id] = snapshot
        return f"{component_id}:{hash(snapshot)}"

    def compare(self, component_id: str, current: CapacitySnapshot) -> dict[str, float]:
        baseline = self._snapshots.get(component_id)
        if not baseline:
            return {}
        return {
            "cpu_delta": current.cpu_pct - baseline.cpu_pct,
            "mem_delta": current.mem_pct - baseline.mem_pct,
            "disk_delta": current.disk_pct - baseline.disk_pct,
        }

    def get_baseline(self, component_id: str) -> CapacitySnapshot | None:
        return self._snapshots.get(component_id)
