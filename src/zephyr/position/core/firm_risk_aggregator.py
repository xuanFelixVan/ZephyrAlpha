# [BLUEPRINT] MOD-POS-021 | docs/03_modules/_domain_position/firm_risk_aggregator/blueprint.md
# [MODULE] zephyr.position.core.firm_risk_aggregator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.strategy_book
# [CONSUMERS] MOD-POS-001(position_sizing_engine消费FirmTargetPortfolio)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 自然叠加(S1给3%+S2给5%=8%); 单票硬上限裁剪按比例削(非按策略优先级截断); 不做MVO不做协方差估计; O(N)复杂度; 冲突标的按净额处理
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AggregationError(ZA-POS-0021); ConstraintViolationError(ZA-POS-0023)
# [TESTS] tests/position/test_firm_risk_aggregator.py
# [A_module] module_id=MOD-POS-021 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FirmRiskAggregator — Firm层风险聚合器 (MOD-POS-021)

A 模型（30_multi_strategy_concurrency §2.2）的组合汇总层。消费所有 StrategyBook 的
TargetPortfolio，**按标的求和（自然叠加）+ 组合级硬上限裁剪 + 冲突净额处理**，
产出 FirmTargetPortfolio 交由 MOD-POS-001 精裁决。

核心哲学（30_multi_strategy_concurrency §2.3）：用加法替代优化器，O(N) 替代 O(N²)。
多策略选到同一只票时仓位自然叠加，等价于永远稳定的等权 risk-budget 优化器。

不做什么：MVO/协方差估计（§3.1 拒绝）/ Kelly（归 MOD-POS-001）/
         选股（归 StrategyBook）/ 跨策略投票（§3.2 拒绝 Model D）

阶段：骨架（接口完整，实现待填充）。
依据: 30_multi_strategy_concurrency §2.2/§2.3/§3.1 + blueprint §2.3
SSoT: depgraph MOD-POS-021
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FirmTarget:
    """单标的汇总后目标（含各策略贡献明细）。"""

    target_weight: float                 # 裁剪后最终权重
    contributions: dict[str, float]      # {strategy_id: 贡献权重}（归因用）
    cut_ratio: float                     # 被裁剪比例（0=未裁剪，0.2=削了20%）


@dataclass(frozen=True)
class ConflictRecord:
    """冲突标的净额处理记录（一策略买一策略卖）。"""

    symbol: str
    buy_strategies: dict[str, float]     # {strategy_id: 买方权重}
    sell_strategies: dict[str, float]    # {strategy_id: 卖方权重}
    net_weight: float                    # 净额


@dataclass(frozen=True)
class FirmTargetPortfolio:
    """组合级汇总目标（CTR-POS-021）。

    所有策略汇总 + 裁剪后的组合级粗仓位，仍未经 Kelly，交由 MOD-POS-001 精裁决。
    """

    firm_positions: dict[str, FirmTarget]
    total_exposure: float                # 所有标的 target_weight 之和
    total_budget: float                  # 所有策略 budget 之和
    cash_ratio: float                    # = total_budget − total_exposure
    constraint_checks: dict[str, Any]    # 单票/行业/总仓位检查结果（含是否触发裁剪）
    conflicts_resolved: list[ConflictRecord] = field(default_factory=list)
    degraded: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    idempotency_key: str = ""
    schema_version: str = "1.0"


class FirmRiskAggregator:
    """Firm 层风险聚合器（MOD-POS-021）。

    使用方式：
        aggregator = FirmRiskAggregator(risk_limits={...})
        firm_target = aggregator.aggregate([tp1, tp2, tp3])

    骨架阶段：方法签名完整，实现待填充。
    """

    def __init__(self, risk_limits: dict[str, Any] | None = None) -> None:
        """初始化。

        Args:
            risk_limits: 硬上限配置（single_name_cap / sector_cap / total_exposure_cap）。
        """
        self.risk_limits = risk_limits or {
            "single_name_cap": 0.08,   # 单票 8%
            "sector_cap": 0.30,        # 行业 30%
            "total_exposure_cap": 0.95,  # 总仓位 95%
        }

    # ── 公共接口 ──────────────────────────────────────────────────────

    def aggregate(
        self,
        target_portfolios: list[Any],  # list[TargetPortfolio]，避免循环导入用 Any
        position_snapshot: dict[str, Any] | None = None,
    ) -> FirmTargetPortfolio:
        """主入口：自然叠加 + 硬上限裁剪 + 冲突净额 → FirmTargetPortfolio。

        步骤（30_multi_strategy_concurrency §2.2 + blueprint §3）：
            1. 按标的求和（自然叠加，S1 给 3% + S2 给 5% = 8%）
            2. 冲突标的净额处理（一策略买一策略卖 → 按净额）
            3. 单票硬上限裁剪（>8% 按比例削，非按策略优先级截断）
            4. 行业集中度裁剪
            5. 总仓位硬约束
        """
        raise NotImplementedError("骨架：待实现求和+净额+三级硬裁剪")

    # ── 子方法（待实现）──────────────────────────────────────────────

    def _sum_by_symbol(self, target_portfolios: list[Any]) -> dict[str, dict[str, float]]:
        """按标的求和（自然叠加），返回 {symbol: {strategy_id: 贡献}}。"""
        raise NotImplementedError("骨架：待实现自然叠加求和")

    def _resolve_conflicts(
        self, symbol_contributions: dict[str, dict[str, float]]
    ) -> tuple[dict[str, float], list[ConflictRecord]]:
        """冲突标的净额处理（买方卖方对冲）。"""
        raise NotImplementedError("骨架：待实现冲突净额")

    def _clip_single_name(
        self, firm_positions: dict[str, FirmTarget]
    ) -> dict[str, FirmTarget]:
        """单票硬上限裁剪（>8% 按比例削，INVARIANTS：非按策略优先级截断）。"""
        raise NotImplementedError("骨架：待实现单票按比例裁剪")

    def _clip_sector(
        self, firm_positions: dict[str, FirmTarget]
    ) -> dict[str, FirmTarget]:
        """行业集中度裁剪。"""
        raise NotImplementedError("骨架：待实现行业裁剪")

    def _clip_total_exposure(
        self, firm_positions: dict[str, FirmTarget]
    ) -> dict[str, FirmTarget]:
        """总仓位硬约束裁剪。"""
        raise NotImplementedError("骨架：待实现总仓位裁剪")
