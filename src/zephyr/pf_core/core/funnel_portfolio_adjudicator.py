# [BLUEPRINT] MOD-PF-010 | docs/03_modules/_domain_portfolio_core/funnel_portfolio_adjudicator/blueprint.md
# [MODULE] zephyr.pf_core.core.funnel_portfolio_adjudicator
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（漏斗第六层→MOD-PF-002/CTR-007 目标组合装配）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] adjusted=score×(1−derate×crowding)(crowding≥warn时); 排序adjusted降序+symbol升序(确定性); |corr|≥limit过滤; 行业≤min(abs_cap,基准+band); 单市值桶≤bucket_cap; σp≤vol_budget且加权MaxDD≤maxdd_budget否则确定性淘汰; |风格暴露|≤style_limit; bearish→总仓×bearish_gross; N≤max_names; 缺失corr按0计并披露; 报告frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FunnelAdjudicationError
# [TESTS] tests/pf_core/test_funnel_portfolio_adjudicator.py
# [A_module] module_id=MOD-PF-010 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Funnel Portfolio Adjudicator — 筛选漏斗第六层：组合优化裁决器 (MOD-PF-010, CAND-PF004-003, B10-01505)

对第五层产出候选施加组合层规则族，输出 N≤10 目标持仓清单（含权重）：
行业±10%/绝对30% + 市值分散 + 波动率与 MaxDD 风险预算 + 风格暴露 ≤±0.3σ +
corr<0.7 过滤 + C-045 拥挤度降权 + C-036 合力偏空整体降仓。

与既有件分工（蓝图 §0 查重裁定）：portfolio_optimizer（MOD-PF-002）=通用凸优化
引擎；strategy_cpcv_matrix（MOD-BT-028）=第五层离线打分；strategy_cross_vote_funnel
（MOD-SIG-109）=第五层在线投票；constraint_solver（MOD-PF-006）=CTR-003 通用约束
投影。本件=漏斗第六层专用规则裁决器，纯函数无 IO，数据全注入。

依据: blueprint.md（MOD-PF-010）§1 规则
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 候选清单 FunnelCandidate
#   fields: symbol/score/industry/market_cap/volatility/max_drawdown/style_loadings/crowding_score
# - id: I2
#   name: 相关性矩阵 + 基准行业权重 + 偏空标记
#   fields: correlations {(a,b):corr}（缺失按0计披露）; benchmark_industry_weights; bearish
# 层: 算法
# - id: A1
#   name_zh: ① 拥挤度降权+确定性排序
#   name_en: _adjusted_score
#   intro: crowding≥warn→score×(1−derate×crowding)；adjusted降序+symbol升序
# - id: A2
#   name_zh: ② 贪心遴选（corr/行业/市值桶）
#   name_en: _greedy_select
#   intro: |corr|≥limit跳过；行业≤min(abs_cap,基准+band)；单桶≤bucket_cap（按1/max_names投影）
# - id: A3
#   name_zh: ③ 风险预算与风格淘汰
#   name_en: _enforce_budgets
#   intro: |风格|超限→淘汰最大贡献者；σp/MaxDD超限→淘汰最低adjusted；重算至满足
# - id: A4
#   name_zh: ④ 偏空降仓与装配
#   name_en: adjudicate
#   intro: bearish→权重×bearish_gross；装 FunnelPortfolioVerdict（frozen）
# 层: 输出
# - id: O1
#   name: FunnelPortfolioVerdict
#   fields: picks(N≤10含权重)/rejected(逐因)/gross_scale/组合诊断/missing_corr_pairs
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "FunnelAdjudicationError",
    "FunnelAdjudicatorConfig",
    "FunnelCandidate",
    "FunnelPick",
    "FunnelPortfolioAdjudicator",
    "FunnelPortfolioVerdict",
    "FunnelRejection",
]


class FunnelAdjudicationError(ZephyrBaseError):
    """漏斗第六层裁决输入/配置非法（Fail-Closed）。

    错误码：ZA-PF-0082（2026-08-26 对账批转正）。
    """

    error_code = "ZA-PF-0082"


class _Cap(str, Enum):
    LARGE = "LARGE"
    MID = "MID"
    SMALL = "SMALL"


@dataclass(frozen=True)
class FunnelAdjudicatorConfig:
    """第六层裁决阈值族（C 类可调）。"""

    max_names: int = 10  # N≤10
    industry_abs_cap: float = 0.30  # 行业绝对上限 30%
    industry_band: float = 0.10  # 基准相对 ±10%
    bucket_cap: float = 0.70  # 单一市值桶占比上限
    large_cap_threshold: float = 1e11  # 大市值 ≥ 1000 亿
    small_cap_threshold: float = 2e10  # 小市值 < 200 亿
    vol_budget: float = 10.0  # 组合波动率预算（默认宽松）
    maxdd_budget: float = 1.0  # 加权 MaxDD 预算（默认宽松）
    style_limit: float = 0.3  # 风格暴露 ≤±0.3σ
    corr_limit: float = 0.7  # |corr|≥0.7 过滤
    crowding_warn: float = 0.7  # C-045 拥挤度降权起点
    crowding_derate: float = 0.5  # 降权系数
    bearish_gross: float = 0.5  # C-036 合力偏空总仓比例

    def __post_init__(self) -> None:
        if not isinstance(self.max_names, int) or self.max_names < 1:
            raise FunnelAdjudicationError(f"max_names 必须 ≥1: {self.max_names}")
        for name in ("industry_abs_cap", "industry_band", "bucket_cap"):
            v = float(getattr(self, name))
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise FunnelAdjudicationError(f"{name} 必须 ∈(0,1]: {v}")
        for name in ("large_cap_threshold", "small_cap_threshold", "vol_budget", "maxdd_budget"):
            v = float(getattr(self, name))
            if not math.isfinite(v) or v <= 0:
                raise FunnelAdjudicationError(f"{name} 必须为正有限值: {v}")
        if not self.small_cap_threshold < self.large_cap_threshold:
            raise FunnelAdjudicationError("small_cap_threshold 必须 < large_cap_threshold")
        for name in ("style_limit", "corr_limit", "bearish_gross"):
            v = float(getattr(self, name))
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise FunnelAdjudicationError(f"{name} 必须 ∈(0,1]: {v}")
        for name in ("crowding_warn", "crowding_derate"):
            v = float(getattr(self, name))
            if not math.isfinite(v) or not 0.0 <= v <= 1.0:
                raise FunnelAdjudicationError(f"{name} 必须 ∈[0,1]: {v}")


@dataclass(frozen=True)
class FunnelCandidate:
    """第六层候选（frozen）。"""

    symbol: str
    score: float
    industry: str
    market_cap: float
    volatility: float
    max_drawdown: float
    style_loadings: Mapping[str, float] = field(default_factory=dict)
    crowding_score: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise FunnelAdjudicationError("symbol 不能为空")
        if not isinstance(self.industry, str) or not self.industry.strip():
            raise FunnelAdjudicationError(f"industry 不能为空: {self.symbol}")
        _require_finite(f"score[{self.symbol}]", self.score)
        mc = _require_finite(f"market_cap[{self.symbol}]", self.market_cap)
        if mc < 0:
            raise FunnelAdjudicationError(f"market_cap 必须 ≥0: {self.symbol}")
        vol = _require_finite(f"volatility[{self.symbol}]", self.volatility)
        if vol < 0:
            raise FunnelAdjudicationError(f"volatility 必须 ≥0: {self.symbol}")
        mdd = _require_finite(f"max_drawdown[{self.symbol}]", self.max_drawdown)
        if mdd < 0:
            raise FunnelAdjudicationError(f"max_drawdown 必须 ≥0: {self.symbol}")
        cs = _require_finite(f"crowding_score[{self.symbol}]", self.crowding_score)
        if not 0.0 <= cs <= 1.0:
            raise FunnelAdjudicationError(f"crowding_score 必须 ∈[0,1]: {self.symbol}={cs}")
        for fct, lv in self.style_loadings.items():
            _require_finite(f"style_loadings[{self.symbol}][{fct}]", lv)


@dataclass(frozen=True)
class FunnelPick:
    """入选标的（frozen）。"""

    symbol: str
    industry: str
    weight: float
    adjusted_score: float


@dataclass(frozen=True)
class FunnelRejection:
    """淘汰留痕（frozen）。"""

    symbol: str
    reason: str


@dataclass(frozen=True)
class FunnelPortfolioVerdict:
    """第六层裁决报告（frozen）。"""

    picks: tuple[FunnelPick, ...]
    rejected: tuple[FunnelRejection, ...]
    gross_scale: float
    portfolio_volatility: float
    portfolio_maxdd: float
    style_exposures: Mapping[str, float]
    missing_corr_pairs: tuple[tuple[str, str], ...]
    notes: tuple[str, ...] = ()


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise FunnelAdjudicationError(f"{name} 必须为有限值: {value}")
    return v


class FunnelPortfolioAdjudicator:
    """筛选漏斗第六层组合优化裁决器（确定性纯函数）。"""

    def __init__(self, config: FunnelAdjudicatorConfig | None = None) -> None:
        self._config = config or FunnelAdjudicatorConfig()

    @property
    def config(self) -> FunnelAdjudicatorConfig:
        return self._config

    def adjudicate(
        self,
        candidates: list[FunnelCandidate] | tuple[FunnelCandidate, ...],
        correlations: Mapping[tuple[str, str], float],
        benchmark_industry_weights: Mapping[str, float] | None = None,
        bearish: bool = False,
    ) -> FunnelPortfolioVerdict:
        """规则族裁决 → N≤10 目标持仓清单。"""
        cfg = self._config
        if not candidates:
            raise FunnelAdjudicationError("candidates 不能为空")
        seen: set[str] = set()
        for c in candidates:
            if not isinstance(c, FunnelCandidate):
                raise FunnelAdjudicationError(f"候选类型非法: {type(c).__name__}")
            if c.symbol in seen:
                raise FunnelAdjudicationError(f"候选 symbol 重复: {c.symbol}")
            seen.add(c.symbol)

        # A1 拥挤度降权 + 确定性排序
        scored = sorted(
            ((self._adjusted(c), c) for c in candidates),
            key=lambda t: (-t[0], t[1].symbol),
        )

        # A2 贪心遴选（corr/行业/市值桶，按 1/max_names 投影）
        w0 = 1.0 / cfg.max_names
        picks: list[tuple[float, FunnelCandidate]] = []
        rejected: list[FunnelRejection] = []
        missing_corr: set[tuple[str, str]] = set()
        industry_count: dict[str, int] = {}
        bucket_count: dict[_Cap, int] = {}
        for adj_score, cand in scored:
            if len(picks) >= cfg.max_names:
                rejected.append(FunnelRejection(cand.symbol, "max_names"))
                continue
            reason = self._check_corr(cand, picks, correlations, missing_corr)
            if reason is None:
                reason = self._check_industry(cand, industry_count, w0, benchmark_industry_weights)
            if reason is None:
                reason = self._check_bucket(cand, bucket_count, w0)
            if reason is not None:
                rejected.append(FunnelRejection(cand.symbol, reason))
                continue
            picks.append((adj_score, cand))
            industry_count[cand.industry] = industry_count.get(cand.industry, 0) + 1
            b = self._bucket(cand.market_cap)
            bucket_count[b] = bucket_count.get(b, 0) + 1

        # A3 风险预算与风格淘汰
        picks, budget_rej = self._enforce_budgets(picks, correlations, missing_corr)
        rejected.extend(budget_rej)

        # A4 偏空降仓 + 装配
        gross_scale = cfg.bearish_gross if bearish else 1.0
        n = len(picks)
        weights = {c.symbol: (gross_scale / n if n else 0.0) for _, c in picks}
        final_picks = tuple(
            FunnelPick(symbol=c.symbol, industry=c.industry, weight=weights[c.symbol], adjusted_score=a)
            for a, c in picks
        )
        syms = [c.symbol for _, c in picks]
        vol = self._portfolio_vol(picks, weights, correlations)
        mdd = sum(weights[c.symbol] * c.max_drawdown for _, c in picks)
        style = self._style_exposures(picks, weights)
        notes: list[str] = []
        if bearish:
            notes.append(f"C-036 合力偏空：总仓降至 {cfg.bearish_gross:.0%}，余为现金")
        if missing_corr:
            notes.append(f"缺失 corr {len(missing_corr)} 对，按 0 计")
        return FunnelPortfolioVerdict(
            picks=final_picks,
            rejected=tuple(rejected),
            gross_scale=gross_scale,
            portfolio_volatility=vol,
            portfolio_maxdd=mdd,
            style_exposures=style,
            missing_corr_pairs=tuple(sorted(missing_corr)),
            notes=tuple(notes),
        )

    # ── 内部 ──

    def _adjusted(self, cand: FunnelCandidate) -> float:
        cfg = self._config
        if cand.crowding_score >= cfg.crowding_warn:
            return cand.score * (1.0 - cfg.crowding_derate * cand.crowding_score)
        return cand.score

    def _corr_of(
        self, a: str, b: str, correlations: Mapping[tuple[str, str], float]
    ) -> float | None:
        if a == b:
            return 1.0
        v = correlations.get((a, b))
        if v is None:
            v = correlations.get((b, a))
        if v is None:
            return None
        return _require_finite(f"corr[{a},{b}]", v)

    def _check_corr(
        self,
        cand: FunnelCandidate,
        picks: list[tuple[float, FunnelCandidate]],
        correlations: Mapping[tuple[str, str], float],
        missing_corr: set[tuple[str, str]],
    ) -> str | None:
        for _, p in picks:
            corr = self._corr_of(cand.symbol, p.symbol, correlations)
            if corr is None:
                missing_corr.add((cand.symbol, p.symbol))
                continue
            if abs(corr) >= self._config.corr_limit:
                return f"corr:{p.symbol}({corr:.2f})"
        return None

    def _check_industry(
        self,
        cand: FunnelCandidate,
        industry_count: dict[str, int],
        w0: float,
        benchmark: Mapping[str, float] | None,
    ) -> str | None:
        cfg = self._config
        limit = cfg.industry_abs_cap
        if benchmark is not None:
            bw = _require_finite(f"benchmark[{cand.industry}]", benchmark.get(cand.industry, 0.0))
            limit = min(limit, bw + cfg.industry_band)
        projected = (industry_count.get(cand.industry, 0) + 1) * w0
        if projected > limit + 1e-12:
            return f"industry_cap:{cand.industry}(>{limit:.2f})"
        return None

    def _bucket(self, market_cap: float) -> _Cap:
        cfg = self._config
        if market_cap >= cfg.large_cap_threshold:
            return _Cap.LARGE
        if market_cap < cfg.small_cap_threshold:
            return _Cap.SMALL
        return _Cap.MID

    def _check_bucket(self, cand: FunnelCandidate, bucket_count: dict[_Cap, int], w0: float) -> str | None:
        b = self._bucket(cand.market_cap)
        projected = (bucket_count.get(b, 0) + 1) * w0
        if projected > self._config.bucket_cap + 1e-12:
            return f"bucket_cap:{b.value}(>{self._config.bucket_cap:.2f})"
        return None

    def _style_exposures(
        self, picks: list[tuple[float, FunnelCandidate]], weights: Mapping[str, float]
    ) -> dict[str, float]:
        out: dict[str, float] = {}
        for _, c in picks:
            for fct, lv in c.style_loadings.items():
                out[fct] = out.get(fct, 0.0) + weights[c.symbol] * lv
        return out

    def _portfolio_vol(
        self,
        picks: list[tuple[float, FunnelCandidate]],
        weights: Mapping[str, float],
        correlations: Mapping[tuple[str, str], float],
    ) -> float:
        var = 0.0
        for _, ci in picks:
            wi = weights[ci.symbol]
            for _, cj in picks:
                wj = weights[cj.symbol]
                corr = self._corr_of(ci.symbol, cj.symbol, correlations)
                rho = 1.0 if ci.symbol == cj.symbol else (corr if corr is not None else 0.0)
                var += wi * wj * rho * ci.volatility * cj.volatility
        return math.sqrt(max(var, 0.0))

    def _enforce_budgets(
        self,
        picks: list[tuple[float, FunnelCandidate]],
        correlations: Mapping[tuple[str, str], float],
        missing_corr: set[tuple[str, str]],
    ) -> tuple[list[tuple[float, FunnelCandidate]], list[FunnelRejection]]:
        cfg = self._config
        picks = list(picks)
        rejected: list[FunnelRejection] = []
        while len(picks) > 1:
            n = len(picks)
            weights = {c.symbol: 1.0 / n for _, c in picks}
            style = self._style_exposures(picks, weights)
            viol_factor = None
            viol_abs = 0.0
            for fct, exp in style.items():
                if abs(exp) > cfg.style_limit and abs(exp) > viol_abs:
                    viol_factor, viol_abs = fct, abs(exp)
            if viol_factor is not None:
                # 淘汰该因子最大贡献者（|w×loading| 最大；同值取 adjusted 最低、symbol 升序）
                drop = min(
                    picks,
                    key=lambda t: (
                        -abs(t[1].style_loadings.get(viol_factor, 0.0)),
                        t[0],
                        t[1].symbol,
                    ),
                )
                picks.remove(drop)
                rejected.append(
                    FunnelRejection(drop[1].symbol, f"style_limit:{viol_factor}(>{cfg.style_limit})")
                )
                continue
            vol = self._portfolio_vol(picks, weights, correlations)
            mdd = sum(weights[c.symbol] * c.max_drawdown for _, c in picks)
            if vol > cfg.vol_budget or mdd > cfg.maxdd_budget:
                drop = min(picks, key=lambda t: (t[0], t[1].symbol))
                picks.remove(drop)
                which = "vol_budget" if vol > cfg.vol_budget else "maxdd_budget"
                rejected.append(FunnelRejection(drop[1].symbol, which))
                continue
            break
        return picks, rejected
