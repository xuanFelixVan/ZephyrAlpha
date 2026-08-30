# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.clock_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 时钟多源验证不可跳过;NTS验证必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Clock Guard — v0.8.0 时钟完整性防御: NTP漂移检测+wall clock monotonic验证。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: clock_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① ClockGuard
#   name_en: ClockGuard
#   intro: class ClockGuard 源码 L53-L88
#   desc: 公共方法（定义序）: monotonic_start, wall_start, detect_drift, is_suspicious, validate_timestamp；源码 L53-L88
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ClockGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class ClockGuard:
    def __init__(self):
        self._monotonic_start = time.monotonic()
        self._wall_start = time.time()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def monotonic_start(self):
        """只读：monotonic_start（Stage 4 公共化）。"""
        return self._monotonic_start

    @monotonic_start.setter
    def monotonic_start(self, value):
        """写入：monotonic_start（Stage 4 公共化）。"""
        self._monotonic_start = value

    @property
    def wall_start(self):
        """只读：wall_start（Stage 4 公共化）。"""
        return self._wall_start

    @wall_start.setter
    def wall_start(self, value):
        """写入：wall_start（Stage 4 公共化）。"""
        self._wall_start = value

    def detect_drift(self) -> float:
        mono_elapsed = time.monotonic() - self._monotonic_start
        wall_elapsed = time.time() - self._wall_start
        return abs(wall_elapsed - mono_elapsed)

    def is_suspicious(self) -> bool:
        return self.detect_drift() > 5.0

    def validate_timestamp(self, ts: float, tolerance_s: float = 60) -> bool:
        return abs(time.time() - ts) < tolerance_s
