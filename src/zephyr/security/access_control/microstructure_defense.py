# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.microstructure_defense
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DEFENSE_STRATEGIES覆盖所有DefenseType;FidelityFactor.composite_ff公式固定
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/governance_e2e/test_gov_microstructure_defense.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
微结构防御——对抗做市/交易微结构攻击的策略与保真度因子。

依据 MOD-INF-018 蓝图定义 5 类微结构攻击威胁及对应反制措施，
并提供基于成交概率/滑点/盘口深度/部分成交的保真度综合评分。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: microstructure_defense.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 DEFAULT_FIDELITY, DEFENSE_STRATEGIES, DefenseStrategy, DefenseType, Fidelit…
#   desc: __init__ import L0；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（3 类）
#   name_en: data classes
#   intro: DefenseType, DefenseStrategy, FidelityFactor
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import Final

from pydantic import BaseModel, Field


@unique
class DefenseType(StrEnum):
    """5 类微结构攻击威胁。"""

    HFT_FRONT_RUN = "HFT_FRONT_RUN"
    STOP_HUNTING = "STOP_HUNTING"
    SPREAD_EXPLOIT = "SPREAD_EXPLOIT"
    ORDER_BOOK_HOLLOW = "ORDER_BOOK_HOLLOW"
    GAPPING = "GAPPING"


class DefenseStrategy(BaseModel):
    """单类威胁的防御策略描述。"""

    defense: DefenseType
    threat: str
    countermeasure: str


# 5 类威胁的 canonical 反制策略（与 DefenseType 一一对应）
_DEFENSE_STRATEGY_DATA: Final[dict[DefenseType, DefenseStrategy]] = {
    DefenseType.HFT_FRONT_RUN: DefenseStrategy(
        defense=DefenseType.HFT_FRONT_RUN,
        threat="Adversarial agent front-runs user orders using latency advantage",
        countermeasure="Enforce order randomization and commit-reveal scheme",
    ),
    DefenseType.STOP_HUNTING: DefenseStrategy(
        defense=DefenseType.STOP_HUNTING,
        threat="Adversarial agent triggers clustered stop-loss orders to capture liquidity",
        countermeasure="Distribute stop-loss levels and apply slippage guard",
    ),
    DefenseType.SPREAD_EXPLOIT: DefenseStrategy(
        defense=DefenseType.SPREAD_EXPLOIT,
        threat="Adversarial agent manipulates bid-ask spread to extract risk-free profit",
        countermeasure="Apply minimum spread floor and inventory-based quoting",
    ),
    DefenseType.ORDER_BOOK_HOLLOW: DefenseStrategy(
        defense=DefenseType.ORDER_BOOK_HOLLOW,
        threat="Adversarial agent posts spoof orders to create false depth signal",
        countermeasure="Require resting-order penalty and cancel-rate monitor",
    ),
    DefenseType.GAPPING: DefenseStrategy(
        defense=DefenseType.GAPPING,
        threat="Adversarial agent induces price gaps to break downstream risk models",
        countermeasure="Enforce price-band circuit breaker and gap-fill monitor",
    ),
}

DEFENSE_STRATEGIES: Final[dict[DefenseType, DefenseStrategy]] = _DEFENSE_STRATEGY_DATA


class FidelityFactor(BaseModel):
    """微结构保真度因子——4 个子因子加权合成的 composite_ff。"""

    fill_probability: float = Field(default=0.85, ge=0.0, le=1.0)
    slippage: float = Field(default=0.30, ge=0.0, le=1.0)
    order_book_depth: float = Field(default=0.20, ge=0.0, le=1.0)
    partial_fill: float = Field(default=0.60, ge=0.0, le=1.0)

    @property
    def composite_ff(self) -> float:
        """加权合成保真度评分——权重 0.30/0.35/0.20/0.15（合 1.0）。"""
        raw = (
            self.fill_probability * 0.30
            + self.slippage * 0.35
            + self.order_book_depth * 0.20
            + self.partial_fill * 0.15
        )
        return round(raw, 4)

    @property
    def description(self) -> str:
        """人类可读的保真度摘要——含 composite_ff 百分比。"""
        return f"composite fidelity = {self.composite_ff * 100:.2f}%"


DEFAULT_FIDELITY: Final[FidelityFactor] = FidelityFactor()


__all__ = [
    "DEFAULT_FIDELITY",
    "DEFENSE_STRATEGIES",
    "DefenseStrategy",
    "DefenseType",
    "FidelityFactor",
]
