# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.error_budget_burst_limiter
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Error Budget Burst限制不可绕过;daily≤20%/hourly≤5%
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Error Budget Burst Limiter — v0.11.0 错误预算Burst限流器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: error_budget_burst_limiter.py
# 层: 算法
# - id: A1
#   name_zh: ① BurstLimiter
#   name_en: BurstLimiter
#   intro: class BurstLimiter 源码 L53-L96
#   desc: 公共方法（定义序）: burst_window_s, max_burst, requests, allow；源码 L53-L96
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: BurstLimiter
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class BurstLimiter:
    def __init__(self):
        self._burst_window_s = 60
        self._max_burst = 10
        self._requests: list[float] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def burst_window_s(self):
        """只读：burst_window_s（Stage 4 公共化）。"""
        return self._burst_window_s

    @burst_window_s.setter
    def burst_window_s(self, value):
        """写入：burst_window_s（Stage 4 公共化）。"""
        self._burst_window_s = value

    @property
    def max_burst(self):
        """只读：max_burst（Stage 4 公共化）。"""
        return self._max_burst

    @max_burst.setter
    def max_burst(self, value):
        """写入：max_burst（Stage 4 公共化）。"""
        self._max_burst = value

    @property
    def requests(self) -> list[float]:
        """只读：requests（Stage 4 公共化）。"""
        return self._requests

    @requests.setter
    def requests(self, value):
        """写入：requests（Stage 4 公共化）。"""
        self._requests = value

    def allow(self) -> bool:
        now = time.time()
        self._requests = [t for t in self._requests if now - t < self._burst_window_s]
        if len(self._requests) >= self._max_burst:
            return False
        self._requests.append(now)
        return True
