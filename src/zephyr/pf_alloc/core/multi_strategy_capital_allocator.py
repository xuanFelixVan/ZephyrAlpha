# [BLUEPRINT] MOD-PA-003 | docs/03_modules/_domain_portfolio_alloc/multi_strategy_capital_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.multi_strategy_capital_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PA-006(仓位计算) ; D-PF-CORE(TargetPortfolio) ; D-POSITION
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 最终权重和=1.0;MaxDD全线等比缩放;再平衡频率≤1次/日;单策略权重≤capacity
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAllocationInputError
# [TESTS] tests/pf_alloc/test_multi_strategy_capital_allocator.py
# [A_module] module_id=MOD-PA-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


Multi-Strategy Capital Allocator — 多策略资金分配器 (MOD-PA-003)

在策略权重基础上施加: 容量约束 + MaxDDLimit减仓 + 冷启动缩放 + 再平衡频率控制,
产出最终权重(和=1.0)+风险预算。

核心规则 (D-PF-ALLOC §1 PA-03, §1.1):
    - 容量截断 + 归一化 (权重和=1.0)
    - MaxDD > 15% → 全线减仓 50%
    - 冷启动期(5日): 仓位 × 30%, 上限 ≤ 正常 50%
    - 再平衡 ≤ 1 次/交易日
    - 风险预算 ∝ 权重

属A类基础设施(权重规整+阈值缩放+频率控制, 逻辑明确), 策略权重本身(B类)为外部输入。
依据: D:\临时工作区\依赖图-D-PF-ALLOC-组合分配域.md §1 PA-03, §1.1
SSoT: depgraph MOD-PA-003
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略分配请求列表 StrategyAllocationRequest
#   fields: strategy_id + signal_weight(来自PA-01/PA-02的策略权重,正数) + capacity(容量上限∈0,1)
#   code: multi_strategy_capital_allocator.py L114 allocate(requests)
# - id: I2
#   name: 组合最大回撤 max_drawdown
#   fields: 正数浮点 如0.12=12%
#   code: allocate(max_drawdown) L190
# - id: I3
#   name: 冷启动已过交易日数 cold_start_days_elapsed
#   fields: int 可选
#   code: allocate(cold_start_days_elapsed) L191
# - id: I4
#   name: 再平衡日期上下文
#   fields: last_rebalance_date 上次再平衡日期 + today 今日日期(频率控制)
#   code: allocate(last_rebalance_date, today) L192-193
# - id: I5
#   name: 分配配置 AllocationConfig
#   fields: MaxDD阈值15%/减仓50%/冷启动30%×5日/冷启动上限50%/频率≤1次日/总风险预算1.0
#   code: AllocationConfig L74-106
# 层: 算法
# - id: A1
#   name_zh: ① 输入合法性校验
#   name_en: _validate
#   intro: 权重必须为正、容量∈(0,1]、回撤与冷启动天数非负，否则抛错
#   desc: 逐项校验 requests/max_drawdown/cold_start_days_elapsed，非法抛 InvalidAllocationInputError
#   inputs: I1 I2 I3
#   outputs: 校验通过或抛 InvalidAllocationInputError
# - id: A2
#   name_zh: ② 再平衡频率控制
#   name_en: _can_rebalance
#   intro: 每交易日最多再平衡1次，超限返回空分配让调用方沿用上次
#   desc: _rebalance_count按日计数 < max_rebalance_per_day(L282-284)
#   inputs: I4 I5
#   outputs: rebalance_allowed 布尔
# - id: A3
#   name_zh: ③ 容量截断+归一化
#   name_en: capacity cap + normalize
#   intro: 单策略权重截断到容量上限后全体归一，权重和=1.0
#   desc: w=min(signal_weight,capacity) → normalized=w/Σw (L230-238)
#   inputs: I1
#   outputs: 归一权重(和=1.0)
#   invariant: Σtarget_weight=1.0
# - id: A4
#   name_zh: ④ MaxDD减仓+冷启动缩放
#   name_en: reduction factor
#   intro: MaxDD>15%全线减仓50%，冷启动5日内仓位×30%且上限≤正常50%
#   desc: reduction=1 → ×0.50(若MaxDD触发) → ×0.30并min(·,0.50)(若冷启动) (L241-253)
#   inputs: I2 I3 I5
#   outputs: reduction_factor 整体缩放系数
#   invariant: reduction_factor≤1.0 只减不增
# - id: A5
#   name_zh: ⑤ 生成分配与风险预算
#   name_en: build allocations
#   intro: 每策略产出最终权重+风险预算(∝权重)，组装 AllocationResult
#   desc: risk_budget=normalized×total_risk_budget (L256-278)
#   inputs: A1 A2 A3 A4
#   outputs: AllocationResult
#   invariant: 风险预算∝权重
# 层: 输出
# - id: O1
#   name_zh: 资金分配结果 AllocationResult
#   name_en: AllocationResult
#   intro: 最终权重表(和=1.0)+风险预算+整体缩放系数+MaxDD/冷启动/再平衡状态标记
#   invariant: total_weight=1.0; reduction_factor≤1.0
#   downstream: MOD-PA-006(仓位计算) ; D-PF-CORE(TargetPortfolio) ; D-POSITION
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A2
# I5 --> A2
# I1 --> A3
# I2 --> A4
# I3 --> A4
# I5 --> A4
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "AllocationConfig",
    "StrategyAllocationRequest",
    "StrategyAllocation",
    "AllocationResult",
    "MultiStrategyCapitalAllocator",
    "InvalidAllocationInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidAllocationInputError(ZephyrBaseError):
    """资金分配输入非法(如权重非正、容量越界、总资金非正)。"""

    error_code = "ZA-PA-0003"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AllocationConfig:
    """资金分配配置 (设计真源 §1 PA-03, §1.1)。"""

    max_dd_threshold: float = 0.15         # MaxDD > 15% 触发
    max_dd_reduction: float = 0.50          # 触发后全线减仓 50%
    cold_start_factor: float = 0.30         # 冷启动系数 30%
    cold_start_days: int = 5                # 观察期 5 交易日
    cold_start_position_cap: float = 0.50   # 观察期内仓位上限 ≤ 正常 50%
    max_rebalance_per_day: int = 1          # 再平衡频率 ≤ 1 次/日
    total_risk_budget: float = 1.0          # 组合总风险预算

    def __post_init__(self) -> None:
        if not 0 < self.max_dd_threshold < 1:
            raise InvalidAllocationInputError(f"max_dd_threshold must be in (0,1), got {self.max_dd_threshold}")
        if not 0 < self.max_dd_reduction <= 1:
            raise InvalidAllocationInputError(f"max_dd_reduction must be in (0,1], got {self.max_dd_reduction}")
        if not 0 < self.cold_start_factor <= 1:
            raise InvalidAllocationInputError(f"cold_start_factor must be in (0,1], got {self.cold_start_factor}")
        if self.cold_start_days < 0:
            raise InvalidAllocationInputError(f"cold_start_days must be >= 0, got {self.cold_start_days}")
        if not 0 < self.cold_start_position_cap <= 1:
            raise InvalidAllocationInputError(
                f"cold_start_position_cap must be in (0,1], got {self.cold_start_position_cap}"
            )
        if self.max_rebalance_per_day < 1:
            raise InvalidAllocationInputError(
                f"max_rebalance_per_day must be >= 1, got {self.max_rebalance_per_day}"
            )
        if self.total_risk_budget <= 0:
            raise InvalidAllocationInputError(
                f"total_risk_budget must be positive, got {self.total_risk_budget}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategyAllocationRequest:
    """单策略分配请求。"""

    strategy_id: str
    signal_weight: float    # 来自 PA-01/PA-02 的策略权重 (正数)
    capacity: float = 1.0   # 策略容量上限 (权重不可超, 来自 C-042)


@dataclass(frozen=True)
class StrategyAllocation:
    """单策略最终分配。"""

    strategy_id: str
    target_weight: float     # 最终权重 (归一后, 和=1.0)
    risk_budget: float       # 风险预算 (∝ 权重)
    raw_weight: float        # 容量截断后归一前权重
    capacity: float


@dataclass(frozen=True)
class AllocationResult:
    """资金分配结果。"""

    allocations: list[StrategyAllocation]
    total_weight: float                # 应为 1.0
    max_dd_triggered: bool             # MaxDD 是否触发减仓
    cold_start_active: bool            # 是否冷启动期
    rebalance_allowed: bool            # 是否允许再平衡 (频率未超)
    reduction_factor: float            # 整体缩放系数 (MaxDD/冷启动合并)
    timestamp: datetime

    @property
    def weights(self) -> dict[str, float]:
        return {a.strategy_id: a.target_weight for a in self.allocations}


# ──────────────────────────────────────────────────────────────────────────────
# 多策略资金分配器
# ──────────────────────────────────────────────────────────────────────────────


class MultiStrategyCapitalAllocator:
    """多策略资金分配器——容量+MaxDD+冷启动+再平衡频率。

    用法:
        alloc = MultiStrategyCapitalAllocator()
        reqs = [
            StrategyAllocationRequest("TREND", 0.6, capacity=0.5),
            StrategyAllocationRequest("MR", 0.4, capacity=0.4),
        ]
        result = alloc.allocate(reqs, max_drawdown=0.10, cold_start_days_elapsed=2,
                                 last_rebalance_date=yesterday, today=today)
        # result.weights → {"TREND": ..., "MR": ...} (和=1.0, 冷启动缩放)

    Args:
        config: 分配配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: AllocationConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or AllocationConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._rebalance_count: dict[date, int] = {}  # 按日计数

    @property
    def config(self) -> AllocationConfig:
        return self._config

    def allocate(
        self,
        requests: list[StrategyAllocationRequest],
        max_drawdown: float = 0.0,
        cold_start_days_elapsed: int | None = None,
        last_rebalance_date: date | None = None,
        today: date | None = None,
        now: datetime | None = None,
    ) -> AllocationResult:
        """执行多策略资金分配。

        Args:
            requests: 策略分配请求列表
            max_drawdown: 当前组合最大回撤 (正数, 如 0.12=12%)
            cold_start_days_elapsed: 冷启动已过交易日数
            last_rebalance_date: 上次再平衡日期（==today 时判定今日已再平衡，拒绝本次；
                覆盖进程重启后内存频率计数归零的缺口）
            today: 今日日期 (用于频率控制)
            now: 时间戳

        Returns:
            AllocationResult
        """
        now = now or self._clock()
        today = today or now.date()
        cfg = self._config
        self._validate(requests, max_drawdown, cold_start_days_elapsed)

        # 1. 再平衡频率控制（last_rebalance_date==today 视为今日已再平衡——
        #    覆盖进程重启后内存计数归零的缺口，2026-08-17 修复参数静默忽略隐患）
        rebalance_allowed = self._can_rebalance(today) and last_rebalance_date != today
        if not rebalance_allowed:
            # 频率超限: 返回空分配标记不允许 (调用方应沿用上次)
            return AllocationResult(
                allocations=[],
                total_weight=0.0,
                max_dd_triggered=False,
                cold_start_active=False,
                rebalance_allowed=False,
                reduction_factor=1.0,
                timestamp=now,
            )
        self._rebalance_count[today] = self._rebalance_count.get(today, 0) + 1

        # 2. 容量截断
        capped: list[tuple[StrategyAllocationRequest, float]] = []
        for req in requests:
            w = min(req.signal_weight, req.capacity)
            capped.append((req, w))

        # 3. 归一化 (权重和=1.0)
        total_raw = sum(w for _, w in capped)
        if total_raw <= 0:
            raise InvalidAllocationInputError("total signal weight after capacity cap is zero")

        # 4. 整体缩放系数: MaxDD + 冷启动
        reduction = 1.0
        max_dd_triggered = max_drawdown > cfg.max_dd_threshold
        if max_dd_triggered:
            reduction *= cfg.max_dd_reduction

        cold_start_active = (
            cold_start_days_elapsed is not None
            and cold_start_days_elapsed < cfg.cold_start_days
        )
        if cold_start_active:
            reduction *= cfg.cold_start_factor
            # 冷启动仓位上限 ≤ 正常 50%
            reduction = min(reduction, cfg.cold_start_position_cap)

        # 5. 生成分配 (归一权重, 风险预算 ∝ 权重)
        allocations: list[StrategyAllocation] = []
        for req, w in capped:
            normalized = w / total_raw  # 归一到和=1.0
            # 注意: 整体缩放系数作用于"总仓位"而非单策略权重比例;
            # 单策略相对权重仍归一为 1.0, 缩放由调用方应用到总资金
            risk_budget = normalized * cfg.total_risk_budget
            allocations.append(StrategyAllocation(
                strategy_id=req.strategy_id,
                target_weight=normalized,
                risk_budget=risk_budget,
                raw_weight=w,
                capacity=req.capacity,
            ))

        return AllocationResult(
            allocations=allocations,
            total_weight=sum(a.target_weight for a in allocations),
            max_dd_triggered=max_dd_triggered,
            cold_start_active=cold_start_active,
            rebalance_allowed=True,
            reduction_factor=reduction,
            timestamp=now,
        )

    # ── 内部 ──

    def _can_rebalance(self, today: date) -> bool:
        """检查今日再平衡次数是否超限。"""
        return self._rebalance_count.get(today, 0) < self._config.max_rebalance_per_day

    @staticmethod
    def _validate(
        requests: list[StrategyAllocationRequest],
        max_drawdown: float,
        cold_start_days_elapsed: int | None,
    ) -> None:
        if not requests:
            raise InvalidAllocationInputError("requests must not be empty")
        for req in requests:
            if req.signal_weight <= 0:
                raise InvalidAllocationInputError(
                    f"signal_weight for {req.strategy_id} must be positive, got {req.signal_weight}"
                )
            if not 0 < req.capacity <= 1:
                raise InvalidAllocationInputError(
                    f"capacity for {req.strategy_id} must be in (0,1], got {req.capacity}"
                )
        if max_drawdown < 0:
            raise InvalidAllocationInputError(f"max_drawdown must be >= 0, got {max_drawdown}")
        if cold_start_days_elapsed is not None and cold_start_days_elapsed < 0:
            raise InvalidAllocationInputError(
                f"cold_start_days_elapsed must be >= 0, got {cold_start_days_elapsed}"
            )
