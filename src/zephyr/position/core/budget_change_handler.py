# [BLUEPRINT] MOD-POS-022 | docs/03_modules/_domain_position/budget_change_handler/blueprint.md
# [MODULE] zephyr.position.core.budget_change_handler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.strategy_book
# [CONSUMERS] MOD-POS-020(StrategyBook收rebalance指令); MOD-POS-021(FirmRiskAggregator收ForcedTrim); RegimeMetaAllocator(收BudgetChangeHandled反馈)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 只处理budget下调(上调简单直接抬高上限); 三级升级Tier1封锁→Tier2策略自主→Tier3强裁; 策略不能说"我不卖"(rebalance_to_budget必返回适配portfolio); convergence_window按换手率差异化; 每级独立事件可log可复盘
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BudgetChangeError(ZA-POS-0022); TierEscalationTimeout(ZA-POS-0024)
# [TESTS] tests/position/test_budget_change_handler.py
# [A_module] module_id=MOD-POS-022 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BudgetChangeHandler — Budget变动处理器 (MOD-POS-022)

A 模型（30_multi_strategy_concurrency §2.4）的执行层。当 RegimeMetaAllocator 产出新
BudgetAllocation 导致某策略 budget 变动时，本模块负责**把 budget 变动落地到
StrategyBook**——三级升级（Tier 1 封锁 → Tier 2 自主 → Tier 3 强裁），确保策略
适配新 budget。

核心原则（30_multi_strategy_concurrency §2.4）：budget 是硬约束，策略的自主权在"怎么适应 budget"，
不在"要不要适应"。**策略不能说"我不卖"**。三级升级而非直接强砍：尊重策略自主权
（决定砍哪个）+ 避免随机时刻强制卖出的高成本。

不做什么：budget 计算（归 RegimeMetaAllocator）/ 选股仓位裁决（归 StrategyBook/MOD-POS-001）
         / 决定砍哪个仓位（Tier 2 策略自主，Tier 3 按比例 dumb）/ 执行交易（归 D-EX-CORE）
         / 处理 budget 上调（上调简单，直接抬高上限自然部署）

阶段：骨架（接口完整，实现待填充）。
依据: 30_multi_strategy_concurrency §2.4 + blueprint §3
SSoT: depgraph MOD-POS-022
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class TierLevel(Enum):
    """三级升级级别（30_multi_strategy_concurrency §2.4）。"""

    TIER_1_LOCK = "tier_1_lock"          # 封锁新仓（立即，被动）
    TIER_2_REBALANCE = "tier_2_rebalance"  # 策略自主 rebalance（建议，策略自主）
    TIER_3_FORCE_TRIM = "tier_3_force_trim"  # 强制裁剪（强制，firm 层）


@dataclass(frozen=True)
class FreezeNewPositions:
    """Tier 1 指令：封锁新仓（CTR-POS-022-F）。"""

    strategy_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass(frozen=True)
class RebalanceRequest:
    """Tier 2 指令：策略自主 rebalance（CTR-POS-022-R）。"""

    strategy_id: str
    new_budget: float
    convergence_window: timedelta        # 按换手率差异化
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass(frozen=True)
class ForcedTrim:
    """Tier 3 指令：强制按比例裁剪（CTR-POS-022-T，dumb but safe）。"""

    strategy_id: str
    trim_ratio: float                    # 裁剪比例（如 0.2 = 所有仓位削 20%）
    reason: str                          # 触发原因（Tier 2 超时 / firm 风险违例）
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass
class TierState:
    """单策略 budget 变动的三级升级状态机。"""

    strategy_id: str
    current_tier: TierLevel
    old_budget: float
    new_budget: float
    tier1_at: datetime | None = None
    tier2_at: datetime | None = None
    tier3_at: datetime | None = None
    converged: bool = False              # 是否已收敛（策略适配完成）


class BudgetChangeHandler:
    """Budget 变动处理器（MOD-POS-022）。

    使用方式：
        handler = BudgetChangeHandler(convergence_windows={"打板": timedelta(days=2), ...})
        handler.handle_budget_change(strategy_id, old_budget, new_budget)

    骨架阶段：方法签名完整，实现待填充。
    """

    def __init__(
        self,
        convergence_windows: dict[str, timedelta] | None = None,
    ) -> None:
        """初始化。

        Args:
            convergence_windows: 各策略 convergence_window（按换手率差异化）。
                30_multi_strategy_concurrency §6.4：打板 1-2 天，多因子 3-5 天，事件驱动 2-3 天。
        """
        self.convergence_windows = convergence_windows or {
            "打板": timedelta(days=2),
            "多因子": timedelta(days=4),
            "事件驱动": timedelta(days=3),
        }
        self._active_states: dict[str, TierState] = {}  # 进行中的升级状态

    # ── 公共接口 ──────────────────────────────────────────────────────

    def handle_budget_change(
        self,
        strategy_id: str,
        old_budget: float,
        new_budget: float,
        strategy_type: str = "多因子",
    ) -> TierState:
        """主入口：处理 budget 下调，启动三级升级。

        只处理 budget 下调（new < old）。上调简单，StrategyBook 直接抬高上限自然部署。

        三级升级（30_multi_strategy_concurrency §2.4）：
            Tier 1（立即）：封锁新仓，现有仓位不动
            Tier 2（Tier 1 后立即）：发 rebalance_to_budget，策略自选砍哪些
            Tier 3（Tier 2 窗口超时 / firm 风险违例）：按比例强行裁剪所有仓位
        """
        if new_budget >= old_budget:
            raise ValueError(f"本模块只处理 budget 下调（{old_budget}→{new_budget}），上调由 StrategyBook 自然部署")
        raise NotImplementedError("骨架：待实现 Tier1 封锁 → Tier2 rebalance → 超时 Tier3 强裁 状态机")

    def check_convergence(self, strategy_id: str, now: datetime | None = None) -> TierState:
        """检查 Tier 2 是否在 convergence_window 内收敛，否则升级 Tier 3。"""
        raise NotImplementedError("骨架：待实现超时检测 + Tier 3 升级")

    # ── 三级指令生成（待实现）────────────────────────────────────────

    def _issue_tier1_freeze(self, strategy_id: str) -> FreezeNewPositions:
        """Tier 1：封锁新仓指令。"""
        raise NotImplementedError("骨架：待实现封锁新仓指令")

    def _issue_tier2_rebalance(
        self, strategy_id: str, new_budget: float, strategy_type: str
    ) -> RebalanceRequest:
        """Tier 2：策略自主 rebalance 请求（含 convergence_window）。"""
        raise NotImplementedError("骨架：待实现 rebalance 请求（按换手率差异化窗口）")

    def _issue_tier3_force_trim(
        self, strategy_id: str, position_snapshot: dict[str, Any]
    ) -> ForcedTrim:
        """Tier 3：强制按比例裁剪（dumb but safe）。"""
        raise NotImplementedError("骨架：待实现按比例强裁（所有仓位 ×trim_ratio）")
