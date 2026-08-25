# [BLUEPRINT] MOD-PA-013 | docs/03_modules/_domain_portfolio_alloc/maxdd_limit_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.maxdd_limit_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D_PF_ALLOC(策略资金分配上游);D_RISK(回撤预算消费)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 最终权重和=1.0(有激活策略时);降档/暂停只减不增;utilization≥1.0→暂停(权重=0);当前回撤缺失/未知策略→Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidMaxDdInputError(未登记错误码-申请中 ZA-PA-0013)
# [TESTS] tests/pf_alloc/test_maxdd_limit_allocator.py
# [A_module] module_id=MOD-PA-013 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""

MaxDdLimit Allocation Strategist — 最大回撤限制分配器 (MOD-PA-013, PA-13)

按各策略最大回撤预算做资金分配：输入各策略回撤预算+当前回撤（源自 D_RISK
drawdown_tracker 的资金曲线追踪），输出资金分配权重+超限降档/暂停动作。

三档动作（utilization = current_dd / max_dd_budget）：
    - utilization < 0.8   NORMAL   原权重
    - 0.8 <= u < 1.0      DERATE   降档 ×0.5
    - u >= 1.0            SUSPEND  暂停 =0

与 MOD-PA-003 区别：PA-003 是组合级一刀切（MaxDD>15% 全线减 50%）；
本模块是**按策略颗粒度**的预算制分配（机构风险预算标准实践）。
依据: construction_backlog_dig.tsv B10-02101（A1 交易决策架构 §30.1.4，裁定=做 P0）
SSoT: depgraph MOD-PA-013
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略回撤预算列表 StrategyDdBudget
#   fields: strategy_id + base_weight(信号权重,正数) + max_dd_budget(回撤预算∈(0,1])
# - id: I2
#   name: 各策略当前回撤 current_drawdowns
#   fields: {strategy_id: 当前回撤幅度(正数,如0.12=12%)}——源自 drawdown_tracker 资金曲线
# - id: I3
#   name: 配置 MaxDdAllocatorConfig
#   fields: derate_threshold(默认0.8) + derate_factor(默认0.5)
# 层: 算法
# - id: A1
#   name_zh: ① 输入校验(Fail-Closed)
#   name_en: _validate
#   intro: 未知策略/缺失当前回撤/负回撤/非法预算→抛 InvalidMaxDdInputError
# - id: A2
#   name_zh: ② 三档动作判定
#   name_en: _classify
#   intro: utilization<0.8→NORMAL ×1.0;[0.8,1.0)→DERATE ×0.5;≥1.0→SUSPEND ×0.0
# - id: A3
#   name_zh: ③ 加权+归一
#   name_en: _normalize
#   intro: w=base_weight×factor → Σw归一(和=1.0);全暂停→全零+all_suspended=True(零除防护)
# 层: 输出
# - id: O1
#   name: MaxDdAllocationResult
#   fields: weights(Σ=1或全零) + actions(三档) + all_suspended
#   invariant: weights只减不增(因子≤1.0);Σ=1.0(有激活)或全零(全暂停)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DdLimitAction",
    "InvalidMaxDdInputError",
    "MaxDdAllocationResult",
    "MaxDdAllocatorConfig",
    "MaxDdLimitAllocator",
    "StrategyDdBudget",
]

logger = logging.getLogger(__name__)


class InvalidMaxDdInputError(ZephyrBaseError):
    """MaxDdLimit 分配输入非法（未知策略/缺失回撤/非法预算，Fail-Closed）。

    错误码 ZA-PA-0013 未登记（申请中，W3 fragment 补登草稿）——类属性暂不声明，
    治理闭环后回补（对齐 MOD-INF-063 先例）。
    """


class DdLimitAction(str, Enum):
    """三档动作（严重度递增）。"""

    NORMAL = "NORMAL"  # utilization < 0.8
    DERATE = "DERATE"  # 0.8 <= utilization < 1.0，降档
    SUSPEND = "SUSPEND"  # utilization >= 1.0，暂停


@dataclass(frozen=True)
class MaxDdAllocatorConfig:
    """分配配置（降档阈值/降档因子）。"""

    derate_threshold: float = 0.8  # utilization 降档触发线
    derate_factor: float = 0.5  # 降档权重因子（<1.0 只减不增）

    def __post_init__(self) -> None:
        if not 0.0 < self.derate_threshold < 1.0:
            raise InvalidMaxDdInputError(f"derate_threshold 须 ∈(0,1): {self.derate_threshold}")
        if not 0.0 < self.derate_factor < 1.0:
            raise InvalidMaxDdInputError(f"derate_factor 须 ∈(0,1): {self.derate_factor}")


@dataclass(frozen=True)
class StrategyDdBudget:
    """单策略回撤预算声明。

    Attributes:
        strategy_id: 策略标识
        base_weight: 基础权重（信号权重，正数；归一前）
        max_dd_budget: 最大回撤预算（正数幅度，如 0.10=10%）
    """

    strategy_id: str
    base_weight: float
    max_dd_budget: float

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise InvalidMaxDdInputError("strategy_id 不能为空")
        if self.base_weight <= 0:
            raise InvalidMaxDdInputError(f"base_weight 须为正: {self.base_weight}")
        if not 0.0 < self.max_dd_budget <= 1.0:
            raise InvalidMaxDdInputError(f"max_dd_budget 须 ∈(0,1]: {self.max_dd_budget}")


@dataclass(frozen=True)
class MaxDdAllocationResult:
    """分配结果。

    Attributes:
        weights: 最终权重（Σ=1.0；全暂停时全零）
        actions: 各策略三档动作
        all_suspended: 全员暂停标记（零除防护）
    """

    weights: dict[str, float]
    actions: dict[str, DdLimitAction]
    all_suspended: bool


class MaxDdLimitAllocator:
    """最大回撤限制分配器（按策略颗粒度，预算制）。

    用法:
        budgets = (StrategyDdBudget("alpha", 0.5, 0.10), ...)
        out = MaxDdLimitAllocator().allocate(budgets, {"alpha": 0.085, ...})
        out.weights / out.actions
    """

    def __init__(self, config: MaxDdAllocatorConfig | None = None) -> None:
        self._config = config or MaxDdAllocatorConfig()

    @property
    def config(self) -> MaxDdAllocatorConfig:
        return self._config

    def allocate(
        self,
        budgets: tuple[StrategyDdBudget, ...] | list[StrategyDdBudget],
        current_drawdowns: dict[str, float],
    ) -> MaxDdAllocationResult:
        """按回撤预算分配资金权重+三档动作。

        Raises
        ------
        InvalidMaxDdInputError
            未知策略/缺失当前回撤/负回撤/空预算列表。
        """
        if not budgets:
            raise InvalidMaxDdInputError("budgets 不能为空")
        ids = [b.strategy_id for b in budgets]
        if len(set(ids)) != len(ids):
            raise InvalidMaxDdInputError(f"strategy_id 重复: {ids}")
        id_set = set(ids)
        unknown = set(current_drawdowns) - id_set
        if unknown:
            raise InvalidMaxDdInputError(f"未知策略: {sorted(unknown)}")
        missing = id_set - set(current_drawdowns)
        if missing:
            raise InvalidMaxDdInputError(f"缺失当前回撤: {sorted(missing)}（风控关键输入，Fail-Closed）")

        cfg = self._config
        actions: dict[str, DdLimitAction] = {}
        raw: dict[str, float] = {}
        for b in budgets:
            dd = current_drawdowns[b.strategy_id]
            if dd < 0:
                raise InvalidMaxDdInputError(f"当前回撤须非负: {b.strategy_id}={dd}")
            utilization = dd / b.max_dd_budget
            if utilization >= 1.0:
                action, factor = DdLimitAction.SUSPEND, 0.0
            elif utilization >= cfg.derate_threshold:
                action, factor = DdLimitAction.DERATE, cfg.derate_factor
            else:
                action, factor = DdLimitAction.NORMAL, 1.0
            actions[b.strategy_id] = action
            raw[b.strategy_id] = b.base_weight * factor

        total = sum(raw.values())
        if total <= 0.0:
            logger.warning("MaxDdLimit: 全员暂停（预算全越界），权重全零")
            return MaxDdAllocationResult(weights={sid: 0.0 for sid in ids}, actions=actions, all_suspended=True)
        weights = {sid: w / total for sid, w in raw.items()}
        return MaxDdAllocationResult(weights=weights, actions=actions, all_suspended=False)


_FINAL_CHECK: Final[str] = "weights Σ=1.0 或全零；因子≤1.0 只减不增"
