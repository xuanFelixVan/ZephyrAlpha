# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.financial_governance.flash_crash_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 闪崩双轨熔断必须可用;MWCB 7/13/20%阈值不可修改
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Flash Crash Guard — v0.12.0 闪崩双轨熔断器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: flash_crash_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① FlashCrashGuard
#   name_en: FlashCrashGuard
#   intro: class FlashCrashGuard 源码 L53-L84
#   desc: 公共方法（定义序）: trip_time, evaluate, tripped, reset；源码 L53-L84
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FlashCrashGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class FlashCrashGuard:
    LIQUIDITY_THRESHOLD = 50.0
    VELOCITY_THRESHOLD = 60.0

    def __init__(self):
        self._tripped = False
        self._trip_time = 0.0

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def trip_time(self):
        """只读：trip_time（Stage 4 公共化）。"""
        return self._trip_time

    @trip_time.setter
    def trip_time(self, value):
        """写入：trip_time（Stage 4 公共化）。"""
        self._trip_time = value

    def evaluate(self, price_drop_pct: float, velocity_pct_per_s: float, bid_ask_spread_pct: float) -> bool:
        if price_drop_pct > self.LIQUIDITY_THRESHOLD or velocity_pct_per_s > self.VELOCITY_THRESHOLD:
            self._tripped = True
            self._trip_time = time.time()
            return True
        return False

    @property
    def tripped(self) -> bool:
        return self._tripped

    def reset(self):
        self._tripped = False
