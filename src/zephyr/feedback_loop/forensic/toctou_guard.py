# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.toctou_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TOCTOU Guard — v0.15.0 R207

Blindspot: State changes between diagnosis and repair execution invalidate diagnosis assumptions.
Risk: R207 — Diagnosis based on t=0 state; repair executes at t=1 when state already changed.

Mitigation: Time-of-Check-Time-of-Use guard: snapshots state at diagnosis, re-validates before action.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: toctou_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① TOCTOUGuard
#   name_en: TOCTOUGuard
#   intro: class TOCTOUGuard 源码 L70-L84
#   desc: 公共方法（定义序）: snapshot, validate；源码 L70-L84
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TOCTOUGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class StateSnapshot:
    snapshot_id: str
    state_hash: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class TOCTOUGuard:
    snapshots: dict[str, StateSnapshot] = field(default_factory=dict)

    def snapshot(self, decision_id: str, state: dict) -> StateSnapshot:
        state_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        snap = StateSnapshot(snapshot_id=decision_id, state_hash=state_hash)
        self.snapshots[decision_id] = snap
        return snap

    def validate(self, decision_id: str, current_state: dict) -> bool:
        snap = self.snapshots.get(decision_id)
        if snap is None:
            return False
        current_hash = hashlib.sha256(json.dumps(current_state, sort_keys=True).encode()).hexdigest()
        return snap.state_hash == current_hash
