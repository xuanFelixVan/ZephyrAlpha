# [BLUEPRINT] MOD-SIG-118 | docs/03_modules/_domain_signal/supply_chain_momentum/blueprint.md
# [MODULE] zephyr.signal_ashare.supply_chain_momentum
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；产业链邻接表/收益序列/回归器/时钟全注入，不 import zephyr 内部件）
# [CONSUMERS] 运行时装配批（统一注入点装配：供应链动量因子层 / 传导异常预警消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 邻接表注入闭合（重复边/自环拒绝）；上游动量因子=Σ边权×Σlead权重×上游收益(领先1-5日)；传导强度R²>5%筛选（注入回归器，未注入Fail-Closed）；传导异常|z|>2σ标记（σ≤0或对齐样本<2不标记）；同输入必同输出（确定性）
# [MODIFY-GUARD] docs/03_modules/_domain_signal/supply_chain_momentum/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SupplyChainMomentumError(占位 ZA-SIG-UNREGISTERED-SUPPLY-CHAIN-MOMENTUM)——邻接表非法/未知标的/收益不足/非有限读数/回归器缺失或异常/非法配置时抛
# [TESTS] tests/signal_ashare/test_supply_chain_momentum.py
# [A_module] module_id=MOD-SIG-118 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SupplyChainMomentumModel — 产业链传导与供应链动量（MOD-SIG-118）。

B10-01376（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-038，A1 模块22）：
产业链邻接表（投入产出关系注入）+ 上游动量因子（客户/供应商收益领先
1-5 日加权）+ 传导强度 R²>5% 筛选（注入回归器）+ 传导异常 >2σ 标记。
Cohen & Frazzini 供应链动量单机版。

纯内存/DI 设计：邻接表/收益映射/回归器/时钟全注入；不触网、不触盘、
无 subprocess。同输入必同输出。非法输入 Fail-Closed 抛
SupplyChainMomentumError。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChainMomentumReport",
    "ConductionAnomaly",
    "LeadLagResult",
    "RegressionResult",
    "SupplyChainLink",
    "SupplyChainMomentumConfig",
    "SupplyChainMomentumError",
    "SupplyChainMomentumModel",
]

_LEAD_DAYS: Final = (1, 2, 3, 4, 5)


class SupplyChainMomentumError(Exception):
    """供应链动量输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-SUPPLY-CHAIN-MOMENTUM。
    """


def _check_finite(name: str, v: float) -> None:
    if isinstance(v, bool) or not math.isfinite(v):
        raise SupplyChainMomentumError(f"{name} 非有限数: {v!r}")


@dataclass(frozen=True)
class SupplyChainLink:
    """产业链边：upstream → downstream（frozen；边权 ∈ (0,1]）。"""

    upstream: str
    downstream: str
    weight: float

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream:
            raise SupplyChainMomentumError("upstream/downstream 不可为空")
        if self.upstream == self.downstream:
            raise SupplyChainMomentumError(f"自环非法: {self.upstream!r}")
        _check_finite("weight", self.weight)
        if not (0.0 < self.weight <= 1.0):
            raise SupplyChainMomentumError(f"weight 须在 (0,1]: {self.weight}")


@dataclass(frozen=True)
class RegressionResult:
    """注入回归器返回契约（frozen；全有限）。"""

    slope: float
    intercept: float
    r_squared: float

    def __post_init__(self) -> None:
        _check_finite("slope", self.slope)
        _check_finite("intercept", self.intercept)
        _check_finite("r_squared", self.r_squared)


@dataclass(frozen=True)
class LeadLagResult:
    """单条边的最优领先期回归结果（frozen）。"""

    upstream: str
    downstream: str
    best_lead_days: int
    slope: float
    intercept: float
    r_squared: float
    passed: bool


@dataclass(frozen=True)
class ConductionAnomaly:
    """传导异常标记（frozen；|z|>z_threshold）。"""

    upstream: str
    downstream: str
    lead_days: int
    predicted: float
    actual: float
    z_score: float
    flagged_at: datetime.datetime


@dataclass(frozen=True)
class SupplyChainMomentumConfig:
    """供应链动量配置（frozen）。"""

    lead_weights: tuple[float, ...] = (1.0, 0.8, 0.6, 0.4, 0.2)
    r2_threshold: float = 0.05
    z_threshold: float = 2.0
    min_returns: int = 6

    def __post_init__(self) -> None:
        if len(self.lead_weights) != len(_LEAD_DAYS):
            raise SupplyChainMomentumError(
                f"lead_weights 长度须为 {len(_LEAD_DAYS)}: {len(self.lead_weights)}"
            )
        for w in self.lead_weights:
            _check_finite("lead_weight", w)
            if w < 0:
                raise SupplyChainMomentumError(f"lead_weight 不可为负: {w}")
        if sum(self.lead_weights) <= 0:
            raise SupplyChainMomentumError("lead_weights 全零非法")
        _check_finite("r2_threshold", self.r2_threshold)
        if not (0.0 < self.r2_threshold < 1.0):
            raise SupplyChainMomentumError(f"r2_threshold 须在 (0,1): {self.r2_threshold}")
        _check_finite("z_threshold", self.z_threshold)
        if self.z_threshold <= 0:
            raise SupplyChainMomentumError(f"z_threshold 必须为正: {self.z_threshold}")
        if isinstance(self.min_returns, bool) or self.min_returns < max(_LEAD_DAYS) + 1:
            raise SupplyChainMomentumError(
                f"min_returns 必须 ≥ {max(_LEAD_DAYS) + 1}: {self.min_returns!r}"
            )


@dataclass(frozen=True)
class ChainMomentumReport:
    """供应链动量报告（frozen）。"""

    symbol: str
    factor: float
    contributions: tuple[tuple[str, float], ...]
    links: tuple[LeadLagResult, ...]
    anomalies: tuple[ConductionAnomaly, ...]
    score: float
    generated_at: datetime.datetime


class SupplyChainMomentumModel:
    """产业链传导与供应链动量模型（邻接表 + 上游动量因子 + R²筛选 + 异常标记）。"""

    def __init__(
        self,
        *,
        links: Sequence[SupplyChainLink],
        config: SupplyChainMomentumConfig | None = None,
        regressor: Callable[[tuple[float, ...], tuple[float, ...]], RegressionResult] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        links = tuple(links)
        if not links:
            raise SupplyChainMomentumError("产业链邻接表为空")
        seen: set[tuple[str, str]] = set()
        adjacency: dict[str, list[tuple[str, float]]] = {}
        for link in links:
            if not isinstance(link, SupplyChainLink):
                raise SupplyChainMomentumError(f"非 SupplyChainLink 元素: {type(link)!r}")
            key = (link.upstream, link.downstream)
            if key in seen:
                raise SupplyChainMomentumError(f"重复边: {key!r}")
            seen.add(key)
            adjacency.setdefault(link.downstream, []).append((link.upstream, link.weight))
        if regressor is None:
            raise SupplyChainMomentumError("回归器未注入（Fail-Closed，禁止旁路拟合）")
        self._adjacency: dict[str, tuple[tuple[str, float], ...]] = {
            d: tuple(sorted(ups)) for d, ups in adjacency.items()
        }
        self._config = config or SupplyChainMomentumConfig()
        self._regressor = regressor
        self._clock = clock or datetime.datetime.now

    # ── 查询 ─────────────────────────────────────────────────────────────

    def adjacency(self, symbol: str) -> tuple[tuple[str, float], ...]:
        """标的的上游邻居视图（按 upstream 字典序，确定性）。"""
        ups = self._adjacency.get(symbol)
        if ups is None:
            raise SupplyChainMomentumError(f"未知标的（无上游边）: {symbol!r}")
        return ups

    # ── 内部：收益校验 ────────────────────────────────────────────────────

    def _returns_of(self, returns_map: Mapping[str, Sequence[float]], symbol: str) -> tuple[float, ...]:
        series = returns_map.get(symbol)
        if series is None:
            raise SupplyChainMomentumError(f"收益序列缺失: {symbol!r}")
        series = tuple(series)
        if len(series) < self._config.min_returns:
            raise SupplyChainMomentumError(
                f"收益序列不足: {symbol!r} {len(series)} < min_returns={self._config.min_returns}"
            )
        for v in series:
            _check_finite(f"return[{symbol}]", v)
        return series

    # ── 上游动量因子（领先 1-5 日加权） ────────────────────────────────────

    def upstream_momentum(
        self,
        symbol: str,
        returns_map: Mapping[str, Sequence[float]],
    ) -> tuple[float, tuple[tuple[str, float], ...]]:
        """上游动量因子=Σ边权×Σlead权重×上游收益（按邻居字典序贡献）。"""
        ups = self.adjacency(symbol)
        weights = self._config.lead_weights
        factor = 0.0
        contributions: list[tuple[str, float]] = []
        for upstream, edge_w in ups:
            series = self._returns_of(returns_map, upstream)
            lead_sum = 0.0
            for lead, lw in zip(_LEAD_DAYS, weights):
                lead_sum += lw * series[-lead]
            contrib = edge_w * lead_sum
            contributions.append((upstream, contrib))
            factor += contrib
        return factor, tuple(contributions)

    # ── 传导强度 R² 筛选（注入回归器） ────────────────────────────────────

    def screen_links(
        self,
        symbol: str,
        returns_map: Mapping[str, Sequence[float]],
    ) -> tuple[LeadLagResult, ...]:
        """对每条上游边按领先 1-5 日回归，取 R² 最大的 lead；R²>阈值 记 passed。"""
        ups = self.adjacency(symbol)
        follower = self._returns_of(returns_map, symbol)
        out: list[LeadLagResult] = []
        for upstream, _edge_w in ups:
            leader = self._returns_of(returns_map, upstream)
            best: LeadLagResult | None = None
            for lead in _LEAD_DAYS:
                xs = tuple(leader[:-lead])
                ys = tuple(follower[lead:])
                if len(xs) != len(ys) or len(xs) < 2:
                    raise SupplyChainMomentumError(
                        f"领先对齐样本不足: lead={lead} n={len(xs)}"
                    )
                try:
                    result = self._regressor(xs, ys)
                except SupplyChainMomentumError:
                    raise
                except Exception as exc:  # noqa: BLE001 — 回归器异常统一包装 Fail-Closed
                    raise SupplyChainMomentumError(f"注入回归器异常: {exc!r}") from exc
                if not isinstance(result, RegressionResult):
                    raise SupplyChainMomentumError(
                        f"回归器返回非法类型: {type(result)!r}"
                    )
                cand = LeadLagResult(
                    upstream=upstream,
                    downstream=symbol,
                    best_lead_days=lead,
                    slope=result.slope,
                    intercept=result.intercept,
                    r_squared=result.r_squared,
                    passed=result.r_squared > self._config.r2_threshold,
                )
                # R² 更大者优先；并列取更小 lead（确定性）
                if best is None or cand.r_squared > best.r_squared:
                    best = cand
            assert best is not None  # _LEAD_DAYS 非空
            out.append(LeadLagResult(
                upstream=best.upstream,
                downstream=best.downstream,
                best_lead_days=best.best_lead_days,
                slope=best.slope,
                intercept=best.intercept,
                r_squared=best.r_squared,
                passed=best.r_squared > self._config.r2_threshold,
            ))
        return tuple(out)

    # ── 传导异常 >2σ 标记 ────────────────────────────────────────────────

    def _anomalies(
        self,
        symbol: str,
        returns_map: Mapping[str, Sequence[float]],
        links: tuple[LeadLagResult, ...],
    ) -> tuple[ConductionAnomaly, ...]:
        follower = self._returns_of(returns_map, symbol)
        out: list[ConductionAnomaly] = []
        for link in links:
            if not link.passed:
                continue
            leader = self._returns_of(returns_map, link.upstream)
            lead = link.best_lead_days
            xs = tuple(leader[:-lead])
            ys = tuple(follower[lead:])
            if len(xs) < 2:
                continue
            residuals = [
                y - (link.intercept + link.slope * x) for x, y in zip(xs, ys)
            ]
            mean = sum(residuals) / len(residuals)
            var = sum((r - mean) ** 2 for r in residuals) / len(residuals)
            sigma = math.sqrt(var)
            if sigma <= 0:
                continue  # 零方差不标记（无离散度语义）
            # 最新已见 follower 收益的对齐预测点为 leader[-1-lead]
            predicted = link.intercept + link.slope * leader[-(lead + 1)]
            actual = follower[-1]
            z = (actual - predicted) / sigma
            if abs(z) > self._config.z_threshold:
                out.append(ConductionAnomaly(
                    upstream=link.upstream,
                    downstream=symbol,
                    lead_days=lead,
                    predicted=predicted,
                    actual=actual,
                    z_score=z,
                    flagged_at=self._clock(),
                ))
                _log.warning(
                    "传导异常: %s→%s lead=%d z=%.3f", link.upstream, symbol, lead, z
                )
        return tuple(out)

    # ── 主入口 ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        symbol: str,
        returns_map: Mapping[str, Sequence[float]],
    ) -> ChainMomentumReport:
        """评估标的上游动量：因子 + R²筛选 + 异常标记 + 截断评分。"""
        if not symbol:
            raise SupplyChainMomentumError("symbol 为空")
        factor, contributions = self.upstream_momentum(symbol, returns_map)
        links = self.screen_links(symbol, returns_map)
        anomalies = self._anomalies(symbol, returns_map, links)
        score = max(-1.0, min(1.0, factor))
        return ChainMomentumReport(
            symbol=symbol,
            factor=factor,
            contributions=contributions,
            links=links,
            anomalies=anomalies,
            score=score,
            generated_at=self._clock(),
        )
