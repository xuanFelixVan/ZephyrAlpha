# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.concurrent_change_deconfliction
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Concurrent Change Deconfliction — v0.16.0 R230

Blindspot: Owner manual change + FLE auto-repair target same config simultaneously.
Risk: R230 — Owner and FLE overwrite each other; final state is neither intended.

Mitigation: Concurrent change detection with optimistic locking and conflict resolution protocol.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: concurrent_change_deconfliction.py
# 层: 算法
# - id: A1
#   name_zh: ① ConcurrentChangeDeconfliction
#   name_en: ConcurrentChangeDeconfliction
#   intro: class ConcurrentChangeDeconfliction 源码 L77-L96
#   desc: 公共方法（定义序）: attempt, recent_conflicts；源码 L77-L96
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ConcurrentChangeDeconfliction
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ChangeSource(str, Enum):
    OWNER = "OWNER"
    FLE = "FLE"
    EXTERNAL = "EXTERNAL"


@dataclass
class ChangeAttempt:
    source: ChangeSource
    resource: str
    version: int
    timestamp: float = field(default_factory=time.time)
    accepted: bool = False


@dataclass
class ConcurrentChangeDeconfliction:
    resource_versions: dict[str, int] = field(default_factory=dict)
    resolution_log: list[ChangeAttempt] = field(default_factory=list)
    conflict_grace_period: float = 5.0

    def attempt(self, source: ChangeSource, resource: str, expected_version: int) -> bool:
        current_version = self.resource_versions.get(resource, 0)
        if expected_version != current_version:
            self.resolution_log.append(
                ChangeAttempt(source=source, resource=resource, version=expected_version, accepted=False)
            )
            return False
        new_version = current_version + 1
        self.resource_versions[resource] = new_version
        self.resolution_log.append(ChangeAttempt(source=source, resource=resource, version=new_version, accepted=True))
        return True

    def recent_conflicts(self) -> list[ChangeAttempt]:
        now = time.time()
        return [a for a in self.resolution_log if not a.accepted and now - a.timestamp < self.conflict_grace_period]
