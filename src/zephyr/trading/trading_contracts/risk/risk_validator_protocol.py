# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_validator_protocol
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ViolationDetail is SSoT for cross-layer risk violation data; l04 re-exports from here
# [MODIFY-GUARD] Changes to ViolationDetail fields MUST sync with risk.risk_validator
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on negative limit_value
# [TESTS] tests/risk/test_risk_validator.py; tests/ex_core/
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: risk_validator_protocol.py
# 层: 算法
# - id: A1
#   name_zh: ① RiskValidatorProtocol
#   name_en: RiskValidatorProtocol
#   intro: class RiskValidatorProtocol 源码 L71-L86
#   desc: 公共方法（定义序）: validate_order, validate_portfolio；源码 L71-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RiskValidatorProtocol
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # 5.145.12 修复：limits: Any -> RiskLimits（SSoT: cross_layer_contracts.yaml CTR-003）
    # TYPE_CHECKING 导入避免运行期循环依赖；from __future__ import annotations 使注解惰性求值
    from zephyr.shared.contracts.risk_limits import RiskLimits


@dataclass(frozen=True)
class ViolationDetail:
    constraint: str
    description: str
    limit_value: Decimal
    actual_value: Decimal
    severity: str = "HALT"


@runtime_checkable
class RiskValidatorProtocol(Protocol):
    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: RiskLimits,
    ) -> list[ViolationDetail]: ...

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: RiskLimits,
    ) -> list[ViolationDetail]: ...


__all__ = ["RiskValidatorProtocol", "ViolationDetail"]
