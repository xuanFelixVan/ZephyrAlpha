# [BLUEPRINT] MOD-POS-020 | docs/03_modules/_domain_position/strategy_book/blueprint.md
# [MODULE] zephyr.position.core.strategy_book
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.drawdown_controller; zephyr.position.core.capital_curve_manager
# [CONSUMERS] MOD-POS-021(FirmRiskAggregator消费TargetPortfolio); MOD-PA-007(RegimeMetaAllocator收PerformanceScore反馈)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] total_weight≤budget(粗仓位不经Kelly); sizing_method∈{equal_weight,risk_parity,custom}禁用Kelly/MVO; 策略不知道市场态只收budget数字; rebalance_to_budget必须返回适配portfolio(策略不能说"我不卖"); DrawdownProtocol四级回撤触发独立收缩
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategySelectionError(ZA-POS-0020); BudgetExceededError(ZA-POS-0021); RebalanceRefusedError(ZA-POS-0022)
# [TESTS] tests/position/test_strategy_book.py
# [A_module] module_id=MOD-POS-020 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StrategyBook — 独立策略账本 (MOD-POS-020)

A 模型（30_multi_strategy_concurrency §2.1）的核心实体。每个策略是一个自洽的 StrategyBook，
自带选股 + 粗仓位（等权/risk parity，**不用 Kelly，不用 MVO**）+ 独立风控，
输出 target_portfolio（标的 + 目标权重）。

分层边界（方案 A，2026-08-06）：
    策略层 StrategyBook（本模块）—— 选股 + 粗仓位
    组合汇总层 FirmRiskAggregator (MOD-POS-021) —— 求和 + 组合级硬裁剪
    组合裁决层 MOD-POS-001 position_sizing_engine —— Kelly + 13 约束

数据流：StrategyBook → FirmRiskAggregator → MOD-POS-001 → 下单

不做什么：Kelly 精裁（归 MOD-POS-001）/ 组合级约束（归 MOD-POS-021）/
         MVO（30_multi_strategy_concurrency §3.1 拒绝）/ 知道市场态（只收 budget 数字）

阶段：骨架（接口完整，实现待填充）。
依据: 30_multi_strategy_concurrency §2.2/§2.4/§2.5 + blueprint §2.3
SSoT: depgraph MOD-POS-020
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TargetWeight:
    """单标的粗仓位权重。"""

    target_weight: float   # 目标权重（粗仓位，未经 Kelly）
    reason: str            # 选入理由
    confidence: float      # 策略自信度 [0, 1]


@dataclass(frozen=True)
class TargetPortfolio:
    """单策略目标组合（CTR-POS-020）。

    粗仓位未经 Kelly，权重和 ≤ budget。与 MOD-POS-001 PositionPlan 的区别：
    TargetPortfolio 是"策略想买什么"，PositionPlan 是"组合最终能买什么"。
    """

    strategy_id: str
    positions: dict[str, TargetWeight]
    total_weight: float                       # ≤ budget，未满部分为现金
    budget: float                             # 当前资金预算占比（来自 RegimeMetaAllocator）
    cash_ratio: float                         # = budget − total_weight
    sizing_method: str                        # equal_weight / risk_parity / custom
    created_at: datetime = field(default_factory=datetime.now)
    idempotency_key: str = ""
    schema_version: str = "1.0"


class StrategyBook:
    """独立策略账本（MOD-POS-020）。

    每个策略继承本类，实现 select_stocks() 提供 alpha 信号。粗仓位由本类按
    sizing_method 计算（等权/risk parity/custom，**不用 Kelly**）。

    骨架阶段：方法签名完整，实现待填充。
    """

    def __init__(
        self,
        strategy_id: str,
        sizing_method: str = "equal_weight",
    ) -> None:
        if sizing_method not in ("equal_weight", "risk_parity", "custom"):
            raise ValueError(f"sizing_method 禁用 {sizing_method}（A 模型不允许 Kelly/MVO）")
        self.strategy_id = strategy_id
        self.sizing_method = sizing_method
        self._current_budget: float = 1.0  # Phase 1 等权占位，Phase 2 来自 RegimeMetaAllocator

    # ── 公共接口 ──────────────────────────────────────────────────────

    def build_target_portfolio(
        self,
        alpha_signals: dict[str, Any],
        position_snapshot: dict[str, Any] | None = None,
    ) -> TargetPortfolio:
        """主入口：选股 + 粗仓位 → TargetPortfolio。

        Args:
            alpha_signals: 策略 alpha 信号（策略 specific）。
            position_snapshot: 当前持仓快照（可选，风控用）。

        Returns:
            TargetPortfolio（粗仓位，未经 Kelly，total_weight ≤ budget）
        """
        selected = self.select_stocks(alpha_signals)
        positions = self.size_positions(selected)
        raise NotImplementedError("骨架：待实现选股+粗仓位+budget裁剪+cash_ratio 计算")

    def rebalance_to_budget(self, new_budget: float) -> TargetPortfolio:
        """适配新 budget（30_multi_strategy_concurrency §2.4，三级升级 Tier 2 调用）。

        策略自主决定砍哪些仓位——**策略不能说"我不卖"**。
        budget 上调时通过买入信号自然部署；下调时砍最不自信的仓位。
        """
        raise NotImplementedError("骨架：待实现 budget 适配（砍最不自信仓位/自然部署新资金）")

    def compute_performance_score(self) -> float:
        """计算自身 60 日滚动 Sharpe → PerformanceScore [0.5, 1.5]。

        供 RegimeMetaAllocator 后验分配（Phase 2）。
        """
        raise NotImplementedError("骨架：待实现 60 日滚动 Sharpe → [0.5,1.5] 映射")

    # ── 子方法（待实现）──────────────────────────────────────────────

    def select_stocks(self, alpha_signals: dict[str, Any]) -> list[str]:
        """策略 alpha 选股（子类实现）。"""
        raise NotImplementedError("骨架：子类实现 alpha 选股逻辑")

    def size_positions(self, symbols: list[str]) -> dict[str, TargetWeight]:
        """粗仓位计算（等权/risk_parity/custom，不用 Kelly）。"""
        raise NotImplementedError(f"骨架：待实现 {self.sizing_method} 粗仓位")
