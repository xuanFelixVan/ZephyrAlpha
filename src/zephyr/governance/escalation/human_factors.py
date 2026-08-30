# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.human_factors
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 疲劳/情绪检测不可禁用;人因告警必须升级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Human Factors — v0.7.0 人因工程: 通知疲劳管理+上下文简洁性+多通道notifications。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: human_factors.py
# 层: 算法
# - id: A1
#   name_zh: ① HumanFactors
#   name_en: HumanFactors
#   intro: class HumanFactors 源码 L53-L104
#   desc: 公共方法（定义序）: notification_count, last_notified, min_interval_s, max_per_hour, should_notify；源码 L53-L104
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: HumanFactors
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time


class HumanFactors:
    def __init__(self):
        self._notification_count: dict[str, int] = {}
        self._last_notified: dict[str, float] = {}
        self._min_interval_s = 300
        self._max_per_hour = 12

    # ── Stage 4 公共化属性 ──

    @property
    def notification_count(self) -> dict[str, int]:
        """每 owner 通知计数（public API, Stage 4）."""
        return self._notification_count

    @property
    def last_notified(self) -> dict[str, float]:
        """每 owner 最近通知时间戳（public API, Stage 4）."""
        return self._last_notified

    @property
    def min_interval_s(self) -> int:
        """最小通知间隔秒数（public API, Stage 4）."""
        return self._min_interval_s

    @min_interval_s.setter
    def min_interval_s(self, value: int) -> None:
        """设置最小通知间隔秒数（for testing, Stage 4）."""
        self._min_interval_s = value

    @property
    def max_per_hour(self) -> int:
        """每小时最大通知数（public API, Stage 4）."""
        return self._max_per_hour

    @max_per_hour.setter
    def max_per_hour(self, value: int) -> None:
        """设置每小时最大通知数（for testing, Stage 4）."""
        self._max_per_hour = value

    def should_notify(self, owner_id: str) -> tuple[bool, str]:
        now = time.time()
        window_start = now - 3600
        recent = [
            t for t_owner, t in [(o, lt) for o, lt in self._last_notified.items() if o == owner_id] if t > window_start
        ]
        if len(recent) >= self._max_per_hour:
            return False, "Rate limited"
        if owner_id in self._last_notified and now - self._last_notified[owner_id] < self._min_interval_s:
            return False, "Too frequent"
        self._last_notified[owner_id] = now
        self._notification_count[owner_id] = self._notification_count.get(owner_id, 0) + 1
        return True, "OK"
