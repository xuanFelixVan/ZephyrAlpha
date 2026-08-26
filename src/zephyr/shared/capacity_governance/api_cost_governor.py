# [BLUEPRINT] MOD-SHARED-003 | docs/03_modules/_domain_shared/api_cost_governor/blueprint.md
# [MODULE] zephyr.shared.capacity_governance.api_cost_governor
# [DOMAIN] D_SHARED
# [DEPENDENCIES] 无（协议核心纯内存；clock 注入；cost_estimator/api_rate_limiter 语义参照不 import）
# [CONSUMERS] 运行时装配批（外部数据源适配层统一计量 / 预算降级标记读侧 / QPS 分配器）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 源须先注册成本单价方可计量/取令牌; 预算按日/月周期键(YYYY-MM-DD|YYYY-MM)确定性归集; 超预算自动置降级标记(不可逆至下周期); 令牌桶有效速率=基准QPS×预算剩余比例(无预算=1.0,已降级=0.0); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_shared/api_cost_governor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ApiCostGovernorError(占位 ZA-SH-UNREGISTERED-COST-GOVERNOR)——空source_id/负单价/未注册源/非法预算/非法令牌数时抛
# [TESTS] tests/shared/capacity_governance/test_api_cost_governor.py
# [A_module] module_id=MOD-SHARED-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ApiCostGovernor — 外部API成本治理器（MOD-SHARED-003）。

B1-00308（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-SHARED-001，C2 C-044）：
外部API调用计量（按源计数/成本单价表）+ 成本预算（日/月预算注册，超预算
自动降级标记）+ QPS 动态分配令牌桶（按预算剩余比例动态调速率，注入时钟）。
OpenTelemetry 计费思想单机化。

查重分工（蓝图 §0）：cost_estimator=单次调用成本估算（本件=按源周期归集与
预算裁定，不做估算模型）；api_rate_limiter=固定速率限流（本件=按预算剩余
比例动态调速，不替代其执行面）；budget_aware_prompt=LLM prompt 预算感知
（域不同零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ApiCostGovernorError",
    "ApiCostGovernor",
    "BudgetPeriod",
    "SourceUsage",
    "TokenBucketView",
]


class ApiCostGovernorError(Exception):
    """成本治理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SH-UNREGISTERED-COST-GOVERNOR。
    """


class BudgetPeriod(str, Enum):
    """预算周期（词表闭合）。"""

    DAILY = "daily"
    MONTHLY = "monthly"


@dataclass(frozen=True)
class SourceUsage:
    """单源用量快照（确定性视图，frozen）。"""

    source_id: str
    total_calls: int
    total_cost: float
    period_costs: tuple[tuple[str, float], ...]  # (周期键, 成本) 按周期键排序
    degraded: bool


@dataclass(frozen=True)
class TokenBucketView:
    """令牌桶快照（观测用，frozen）。"""

    source_id: str
    tokens: float
    capacity: float
    effective_rate: float


@dataclass
class _SourceState:
    """单源内部状态（计量 + 预算周期归集 + 令牌桶）。"""

    unit_cost: float
    base_qps: float
    total_calls: int = 0
    total_cost: float = 0.0
    period_costs: dict[str, float] = field(default_factory=dict)
    budgets: dict[BudgetPeriod, float] = field(default_factory=dict)
    degraded: bool = False
    tokens: float = 0.0
    last_refill: datetime.datetime | None = None


class ApiCostGovernor:
    """外部API成本治理器（计量 + 预算降级 + 动态令牌桶）。"""

    def __init__(self, *, clock: Callable[[], datetime.datetime] | None = None) -> None:
        self._clock = clock or datetime.datetime.now
        self._sources: dict[str, _SourceState] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _state_of(self, source_id: str) -> _SourceState:
        state = self._sources.get(source_id)
        if state is None:
            raise ApiCostGovernorError(f"未注册源: {source_id!r}（须先 register_source）")
        return state

    def _period_keys(self, now: datetime.datetime) -> dict[BudgetPeriod, str]:
        """周期键（确定性）：日=YYYY-MM-DD，月=YYYY-MM。"""
        return {
            BudgetPeriod.DAILY: now.strftime("%Y-%m-%d"),
            BudgetPeriod.MONTHLY: now.strftime("%Y-%m"),
        }

    def _remaining_ratio(self, state: _SourceState, now: datetime.datetime) -> float:
        """预算剩余比例：min(各周期剩余/限额)；无预算=1.0；已降级=0.0。"""
        if state.degraded:
            return 0.0
        if not state.budgets:
            return 1.0
        keys = self._period_keys(now)
        ratio = 1.0
        for period, limit in state.budgets.items():
            if limit <= 0:
                return 0.0
            used = state.period_costs.get(keys[period], 0.0)
            ratio = min(ratio, max(0.0, (limit - used) / limit))
        return ratio

    # ── 注册 ─────────────────────────────────────────────────────────────

    def register_source(self, source_id: str, *, unit_cost: float, base_qps: float) -> None:
        """注册源成本单价与基准QPS（幂等重注册同参数；改参数拒绝防歧义）。"""
        if not source_id:
            raise ApiCostGovernorError("source_id 为空")
        if unit_cost < 0:
            raise ApiCostGovernorError(f"unit_cost 非法: {unit_cost!r}（须 ≥ 0）")
        if base_qps <= 0:
            raise ApiCostGovernorError(f"base_qps 非法: {base_qps!r}（须 > 0）")
        existing = self._sources.get(source_id)
        if existing is not None:
            if existing.unit_cost != unit_cost or existing.base_qps != base_qps:
                raise ApiCostGovernorError(
                    f"源 {source_id!r} 已注册且参数冲突（单价/基准QPS 不可变）"
                )
            return  # 同参数幂等
        state = _SourceState(unit_cost=float(unit_cost), base_qps=float(base_qps))
        state.tokens = float(base_qps)  # 满桶启动（容量=基准QPS，即 1s 突发）
        self._sources[source_id] = state

    def register_budget(self, source_id: str, period: BudgetPeriod, limit: float) -> None:
        """注册日/月成本预算（同周期重复注册拒绝，防预算漂移）。"""
        if not isinstance(period, BudgetPeriod):
            raise ApiCostGovernorError(f"非法预算周期: {period!r}")
        if limit <= 0:
            raise ApiCostGovernorError(f"预算限额非法: {limit!r}（须 > 0）")
        state = self._state_of(source_id)
        if period in state.budgets:
            raise ApiCostGovernorError(
                f"源 {source_id!r} 周期 {period.value} 预算已注册（不可重复注册）"
            )
        state.budgets[period] = float(limit)

    # ── 计量 ─────────────────────────────────────────────────────────────

    def record_call(self, source_id: str, *, units: int = 1) -> bool:
        """计量一次调用：累计计数/成本/周期归集；超预算自动置降级标记。

        返回调用后该源是否处于降级状态。
        """
        if units <= 0:
            raise ApiCostGovernorError(f"units 非法: {units!r}（须 > 0）")
        state = self._state_of(source_id)
        now = self._clock()
        cost = state.unit_cost * units
        state.total_calls += units
        state.total_cost += cost
        keys = self._period_keys(now)
        for period, limit in state.budgets.items():
            key = keys[period]
            state.period_costs[key] = state.period_costs.get(key, 0.0) + cost
            if state.period_costs[key] > limit and not state.degraded:
                state.degraded = True
                _log.warning(
                    "源 %s 超 %s 预算（%.4f > %.4f），自动降级标记",
                    source_id, period.value, state.period_costs[key], limit,
                )
        return state.degraded

    def is_degraded(self, source_id: str) -> bool:
        """降级标记查询（未注册源 Fail-Closed）。"""
        return self._state_of(source_id).degraded

    def usage(self, source_id: str) -> SourceUsage:
        """用量快照（周期键确定性排序）。"""
        state = self._state_of(source_id)
        return SourceUsage(
            source_id=source_id,
            total_calls=state.total_calls,
            total_cost=state.total_cost,
            period_costs=tuple(sorted(state.period_costs.items())),
            degraded=state.degraded,
        )

    # ── QPS 动态令牌桶 ────────────────────────────────────────────────────

    def _refill(self, state: _SourceState, now: datetime.datetime) -> None:
        if state.last_refill is None:
            state.last_refill = now
            return
        elapsed = (now - state.last_refill).total_seconds()
        if elapsed < 0:
            raise ApiCostGovernorError("时钟回拨（last_refill 在未来，违反单调性）")
        rate = state.base_qps * self._remaining_ratio(state, now)
        state.tokens = min(state.base_qps, state.tokens + elapsed * rate)
        state.last_refill = now

    def try_acquire(self, source_id: str, *, tokens: int = 1) -> bool:
        """取令牌：先按注入时钟补充（速率=基准QPS×剩余比例），够则扣减放行。"""
        if tokens <= 0:
            raise ApiCostGovernorError(f"tokens 非法: {tokens!r}（须 > 0）")
        state = self._state_of(source_id)
        now = self._clock()
        self._refill(state, now)
        if state.tokens >= tokens:
            state.tokens -= tokens
            return True
        return False

    def bucket_view(self, source_id: str) -> TokenBucketView:
        """令牌桶快照（先触发一次补充以反映当前时刻）。"""
        state = self._state_of(source_id)
        now = self._clock()
        self._refill(state, now)
        return TokenBucketView(
            source_id=source_id,
            tokens=state.tokens,
            capacity=state.base_qps,
            effective_rate=state.base_qps * self._remaining_ratio(state, now),
        )

    def sources(self) -> tuple[str, ...]:
        """已注册源清单（确定性排序）。"""
        return tuple(sorted(self._sources))

    def budget_of(self, source_id: str) -> Mapping[BudgetPeriod, float]:
        """源预算视图（只读副本）。"""
        return dict(self._state_of(source_id).budgets)
