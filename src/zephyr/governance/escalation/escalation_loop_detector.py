# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_loop_detector
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 跨模块循环检测不可跳过;DFS必须覆盖所有活跃升级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Escalation Loop Detector — v0.10.0 跨模块升级循环: escalate->block->auto_guard->escalate循环检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: escalation_loop_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① EscalationLoopDetector
#   name_en: EscalationLoopDetector
#   intro: class EscalationLoopDetector 源码 L53-L78
#   desc: 公共方法（定义序）: history, record_transition, detect_loop；源码 L53-L78
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EscalationLoopDetector
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class EscalationLoopDetector:
    def __init__(self):
        self._history: list[tuple[str, str, float]] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def history(self) -> list[tuple[str, str, float]]:
        """只读：history（Stage 4 公共化）。"""
        return self._history

    @history.setter
    def history(self, value):
        """写入：history（Stage 4 公共化）。"""
        self._history = value

    def record_transition(self, task_id: str, from_level: str, to_level: str):
        self._history.append((task_id, from_level, time.time()))
        self._history.append((task_id, to_level, time.time()))

    def detect_loop(self, window_s: float = 300) -> bool:
        recent = [(tid, lvl) for tid, lvl, t in self._history if time.time() - t < window_s]
        for tid in set(t[0] for t in recent):
            count = sum(1 for t in recent if t[0] == tid)
            if count >= 6:
                return True
        return False
