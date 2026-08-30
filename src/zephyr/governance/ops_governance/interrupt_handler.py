# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.interrupt_handler
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter;zephyr.trading
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬中断必须立即生效;紧急覆盖必须审计记录
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Interrupt Handler — D-022-06 硬中断处理器: Owner紧急中断+优雅停止+状态保存。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: interrupt_handler.py
# 层: 算法
# - id: A1
#   name_zh: ① InterruptHandler
#   name_en: InterruptHandler
#   intro: class InterruptHandler 源码 L60-L90
#   desc: 公共方法（定义序）: signal, interrupt, interrupted, save_state, resume；源码 L60-L90
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: InterruptHandler
#   downstream: zephyr.governance.services.adapter;zephyr.trading
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class InterruptSignal(Enum):
    OWNER_OVERRIDE = "owner_override"
    SAFETY_BREACH = "safety_breach"
    HARD_TIMEOUT = "hard_timeout"


class InterruptHandler:
    def __init__(self):
        self._interrupted = False
        self._signal: InterruptSignal | None = None

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def signal(self) -> InterruptSignal | None:
        """只读：signal（Stage 4 公共化）。"""
        return self._signal

    @signal.setter
    def signal(self, value):
        """写入：signal（Stage 4 公共化）。"""
        self._signal = value

    def interrupt(self, signal: InterruptSignal) -> None:
        self._interrupted = True
        self._signal = signal

    @property
    def interrupted(self) -> bool:
        return self._interrupted

    def save_state(self) -> dict:
        return {"interrupted": self._interrupted, "signal": self._signal.value if self._signal else None}

    def resume(self) -> bool:
        self._interrupted = False
        self._signal = None
        return True
