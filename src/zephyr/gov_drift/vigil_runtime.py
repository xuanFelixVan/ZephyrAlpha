# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_drift.vigil_runtime
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] VIGIL运行时不可禁用;Core Identity不可修改
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Vigil Runtime — v0.6.0 VIGIL维护运行时: 运维token预算+手动override窗口。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: vigil_runtime.py
# 层: 算法
# - id: A1
#   name_zh: ① VigilRuntime
#   name_en: VigilRuntime
#   intro: class VigilRuntime 源码 L53-L116
#   desc: 公共方法（定义序）: override_expiry, override_window_open, token_budget, tokens_used, consume, open_override_window, o…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: VigilRuntime
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class VigilRuntime:
    def __init__(self):
        self._token_budget = 2000
        self._tokens_used = 0
        self._override_window_open = False
        self._override_expiry = 0.0

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def override_expiry(self):
        """只读：override_expiry（Stage 4 公共化）。"""
        return self._override_expiry

    @override_expiry.setter
    def override_expiry(self, value):
        """写入：override_expiry（Stage 4 公共化）。"""
        self._override_expiry = value

    @property
    def override_window_open(self):
        """只读：override_window_open（Stage 4 公共化）。"""
        return self._override_window_open

    @override_window_open.setter
    def override_window_open(self, value):
        """写入：override_window_open（Stage 4 公共化）。"""
        self._override_window_open = value

    @property
    def token_budget(self):
        """只读：token_budget（Stage 4 公共化）。"""
        return self._token_budget

    @token_budget.setter
    def token_budget(self, value):
        """写入：token_budget（Stage 4 公共化）。"""
        self._token_budget = value

    @property
    def tokens_used(self):
        """只读：tokens_used（Stage 4 公共化）。"""
        return self._tokens_used

    @tokens_used.setter
    def tokens_used(self, value):
        """写入：tokens_used（Stage 4 公共化）。"""
        self._tokens_used = value

    def consume(self, tokens: int) -> bool:
        if self._tokens_used + tokens > self._token_budget:
            return False
        self._tokens_used += tokens
        return True

    def open_override_window(self, duration_s: float = 600):
        self._override_window_open = True
        self._override_expiry = time.time() + duration_s

    @property
    def override_active(self) -> bool:
        return self._override_window_open and time.time() < self._override_expiry

    def remaining_tokens(self) -> int:
        return max(0, self._token_budget - self._tokens_used)
