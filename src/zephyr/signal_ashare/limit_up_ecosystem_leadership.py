# [BLUEPRINT] MOD-SIG-097 | docs/03_modules/_domain_signal/limit_up_ecosystem_leadership/blueprint.md
# [MODULE] zephyr.signal_ashare.limit_up_ecosystem_leadership
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；连板梯队快照与收益序列鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：买入侧信号装配层、情绪页涨停板生态卡）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 梯队分布键=1..height_cap 封闭集（cap 层归并 ≥cap）；断层=高度≥2 梯队中计数 0 而其上仍有更高层；晋级率=相邻日同符号 h→h+1 占比∈[0,1]；leadership=Σ|β_lag|≥0；Granger PIT（仅 leader 滞后项解释 follower 当期）；样本不足 checked=False 显式降级不阻断；frozen dataclass asdict JSON 可序列化；纯统计核不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01366 行 + 候选注册表 CAND-TESTB-012
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法连板高度(<1)/负封板分钟/负金额/收益序列不等长/非有限值/lag<1/配置越界 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_limit_up_ecosystem_leadership.py
# [A_module] module_id=MOD-SIG-097 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""动量领导因子与涨停板生态模型（MOD-SIG-097，B10-01366）。

场内对账：limit_up_followthrough（MOD-SIG-078）= 昨涨停/炸板池今日表现统计、
lhb_premium_analyzer（MOD-SIG-057）= 龙虎榜席位溢价；**连板高度因子/封板时间因子/
梯队断层/Granger 领导-跟随系数无实现**（深挖批 min_build_spec 明示缺口），本模块落地。

两件套：

- **涨停板生态快照**：连板高度（max consec_limit）+ 梯队分布（1..cap 封闭集，
  cap 层归并 ≥cap）+ 梯队断层（计数 0 而其上仍有更高层 → fault 层清单 + 严重度）
  + 封板时间因子（first_seal_minute 均值/中位/早盘封板占比，越早越强）
  + 晋级成功率（相邻两日同符号 h→h+1 对齐，2进3<30% 等阈值预警，基数门槛防小样本噪声）。
- **Granger 领导-跟随系数**：leader/follower 收益序列滞后 OLS F 检验
  （受限=自身滞后 vs 非受限=自身+leader 滞后），F 右尾 p 值纯 Python 正则化
  不完全贝塔（连分式）实现——零 scipy（pyproject 幽灵依赖纪律，#ARCH-235 在案，
  与 MOD-SIG-094 同构）；p<significance 且 leadership=Σ|β_lag|>threshold（默认 0.3）
  → 领导关系成立；样本不足 checked=False 显式降级不阻断。

与 cross_market_conduction_sensor（跨市场指数间传导）粒度正交：本件为个股对个股。

依据: AUD-DRAFT-001 深挖批 B10-01366（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-097
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 当日连板梯队快照 list[LimitUpStock]（可选相邻昨日快照）/ leader+follower 收益序列
# 特征: 连板高度分布 + 封板分钟分布 + 同符号晋级对齐 + 滞后收益回归
# 算法: 分布/断层/封板统计 → 晋级率查表预警；受限/非受限 OLS → F 检验（不完全贝塔 p 值）
# 输出: LadderSnapshot（高度/分布/断层/封板/晋级/预警）+ LeadershipCoefficient（F/p/系数/方向）
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "LadderEcosystemConfig",
    "LadderSnapshot",
    "LeadershipCoefficient",
    "LimitUpEcosystemLeadership",
    "LimitUpStock",
]

_BETACF_EPS: Final = 3e-14
_BETACF_MAX_ITER: Final = 200
_TINY: Final = 1e-300
_RSS_EPS: Final = 1e-12
_PIVOT_EPS: Final = 1e-12


# ------------------------------------------------------------------
# 纯 Python F 分布右尾（正则化不完全贝塔，Numerical Recipes 连分式；
# 与 MOD-SIG-094 同构自实现——零 scipy 幽灵依赖纪律，#ARCH-235）
# ------------------------------------------------------------------
def _betacf(a: float, b: float, x: float) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _TINY:
        d = _TINY
    d = 1.0 / d
    h = d
    for m in range(1, _BETACF_MAX_ITER + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _TINY:
            d = _TINY
        c = 1.0 + aa / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _BETACF_EPS:
            break
    return h


def _ibeta(a: float, b: float, x: float) -> float:
    """正则化不完全贝塔 I_x(a,b)。"""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _f_sf(f_stat: float, d1: int, d2: int) -> float:
    """F 分布右尾 P(F>f) = I_{d2/(d2+d1·f)}(d2/2, d1/2)。"""
    if f_stat <= 0.0:
        return 1.0
    x = d2 / (d2 + d1 * f_stat)
    return _ibeta(d2 / 2.0, d1 / 2.0, x)


def _ols_solve(design: list[list[float]], y: list[float]) -> tuple[list[float], float]:
    """正规方程 (X'X)β=X'y 高斯消元（部分主元）+ RSS；矩阵奇异 → ValueError。"""
    n = len(y)
    k = len(design[0])
    xtx = [[0.0] * k for _ in range(k)]
    xty = [0.0] * k
    for i in range(n):
        row = design[i]
        for a in range(k):
            xty[a] += row[a] * y[i]
            for b in range(a, k):
                xtx[a][b] += row[a] * row[b]
    for a in range(k):
        for b in range(a):
            xtx[a][b] = xtx[b][a]
    # 增广矩阵高斯消元（部分主元）
    aug = [xtx[a] + [xty[a]] for a in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(aug[r][col]))
        if abs(aug[piv][col]) < _PIVOT_EPS:
            msg = "设计矩阵奇异（常数列/完全共线）"
            raise ValueError(msg)
        aug[col], aug[piv] = aug[piv], aug[col]
        for r in range(k):
            if r != col and abs(aug[r][col]) > 0.0:
                factor = aug[r][col] / aug[col][col]
                for c in range(col, k + 1):
                    aug[r][c] -= factor * aug[col][c]
    beta = [aug[a][k] / aug[a][a] for a in range(k)]
    rss = 0.0
    for i in range(n):
        resid = y[i] - sum(beta[a] * design[i][a] for a in range(k))
        rss += resid * resid
    return beta, rss


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class LimitUpStock:
    """单票涨停快照（鸭子类型输入；first_seal_minute=自 9:30 起分钟数）。"""

    symbol: str
    consec_limit: int
    first_seal_minute: float | None = None
    amount: float | None = None


@dataclass(frozen=True)
class LadderEcosystemConfig:
    """阈值与查表配置（构造即校验，fail-closed）。"""

    height_cap: int = 5
    seal_early_minute: float = 60.0
    promotion_warn_threshold: float = 0.3
    promotion_min_base: int = 3
    granger_threshold: float = 0.3
    granger_significance: float = 0.05
    granger_max_lag: int = 5
    granger_min_samples: int = 30

    def __post_init__(self) -> None:
        if self.height_cap < 2:
            msg = f"height_cap 须≥2，实得 {self.height_cap}"
            raise ValueError(msg)
        if self.seal_early_minute <= 0.0:
            msg = f"seal_early_minute 须>0，实得 {self.seal_early_minute}"
            raise ValueError(msg)
        if not (0.0 < self.promotion_warn_threshold < 1.0):
            msg = f"promotion_warn_threshold 须∈(0,1)，实得 {self.promotion_warn_threshold}"
            raise ValueError(msg)
        if self.promotion_min_base < 1:
            msg = f"promotion_min_base 须≥1，实得 {self.promotion_min_base}"
            raise ValueError(msg)
        if self.granger_threshold <= 0.0:
            msg = f"granger_threshold 须>0，实得 {self.granger_threshold}"
            raise ValueError(msg)
        if not (0.0 < self.granger_significance < 1.0):
            msg = f"granger_significance 须∈(0,1)，实得 {self.granger_significance}"
            raise ValueError(msg)
        if self.granger_max_lag < 1:
            msg = f"granger_max_lag 须≥1，实得 {self.granger_max_lag}"
            raise ValueError(msg)
        if self.granger_min_samples < 4 * self.granger_max_lag + 10:
            msg = (
                f"granger_min_samples 须≥4×lag+10={4 * self.granger_max_lag + 10}，"
                f"实得 {self.granger_min_samples}"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class LadderSnapshot:
    """涨停板生态快照输出。"""

    trade_date: str | None
    stock_count: int
    max_height: int
    height_distribution: dict[int, int]
    fault_levels: tuple[int, ...]
    fault_severity: float | None
    seal_time_mean: float | None
    seal_time_median: float | None
    early_seal_ratio: float | None
    promotion_rates: dict[int, float] | None
    promotion_warnings: tuple[str, ...]
    degraded: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["height_distribution"] = {str(k): v for k, v in self.height_distribution.items()}
        if self.promotion_rates is not None:
            d["promotion_rates"] = {str(k): v for k, v in self.promotion_rates.items()}
        return d


@dataclass(frozen=True)
class LeadershipCoefficient:
    """Granger 领导-跟随系数输出（leader→follower 单方向）。"""

    checked: bool
    f_stat: float | None
    p_value: float | None
    leadership: float | None
    is_leader: bool
    best_lag: int | None
    n_samples: int
    direction: str
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class LimitUpEcosystemLeadership:
    """涨停板生态快照 + Granger 领导-跟随系数引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: LadderEcosystemConfig | None = None) -> None:
        self._config = config if config is not None else LadderEcosystemConfig()

    @property
    def config(self) -> LadderEcosystemConfig:
        return self._config

    # ── 涨停板生态快照 ─────────────────────────────────────────────
    def ecosystem_snapshot(
        self,
        stocks: Sequence[LimitUpStock],
        *,
        trade_date: str | None = None,
        prev_stocks: Sequence[LimitUpStock] | None = None,
    ) -> LadderSnapshot:
        cfg = self._config
        notes: list[str] = []
        for s in stocks:
            if s.consec_limit < 1:
                msg = f"consec_limit 须≥1，实得 {s.consec_limit}（symbol={s.symbol}）"
                raise ValueError(msg)
            if s.first_seal_minute is not None and s.first_seal_minute < 0.0:
                msg = f"first_seal_minute 须≥0，实得 {s.first_seal_minute}（symbol={s.symbol}）"
                raise ValueError(msg)
            if s.amount is not None and s.amount < 0.0:
                msg = f"amount 须≥0，实得 {s.amount}（symbol={s.symbol}）"
                raise ValueError(msg)

        if not stocks:
            return LadderSnapshot(
                trade_date=trade_date,
                stock_count=0,
                max_height=0,
                height_distribution={h: 0 for h in range(1, cfg.height_cap + 1)},
                fault_levels=(),
                fault_severity=None,
                seal_time_mean=None,
                seal_time_median=None,
                early_seal_ratio=None,
                promotion_rates=None,
                promotion_warnings=(),
                degraded=True,
                notes=("当日零涨停（空梯队）",),
            )

        distribution = {h: 0 for h in range(1, cfg.height_cap + 1)}
        for s in stocks:
            distribution[min(s.consec_limit, cfg.height_cap)] += 1
        max_height = max(s.consec_limit for s in stocks)

        # 断层：eff_top 内计数 0 而其上仍有更高层（cap 层为归并层不判其上）
        eff_top = min(max_height, cfg.height_cap)
        faults = tuple(h for h in range(2, eff_top) if distribution[h] == 0)
        severity: float | None = None
        if eff_top >= 2:
            severity = len(faults) / (eff_top - 1)

        # 封板时间因子（缺数据的票跳过该腿）
        seals = [s.first_seal_minute for s in stocks if s.first_seal_minute is not None]
        seal_mean = seal_median = early_ratio = None
        if seals:
            seal_mean = statistics.fmean(seals)
            seal_median = statistics.median(seals)
            early_ratio = sum(1 for v in seals if v <= cfg.seal_early_minute) / len(seals)
            if len(seals) < len(stocks):
                notes.append(f"封板时间缺失 {len(stocks) - len(seals)}/{len(stocks)} 票，统计仅覆盖在案票")
        else:
            notes.append("封板时间全缺失，封板时间因子腿降级")

        # 晋级成功率（相邻日同符号 h→h+1 对齐）
        promotion_rates: dict[int, float] | None = None
        warnings: list[str] = []
        if prev_stocks is not None:
            for s in prev_stocks:
                if s.consec_limit < 1:
                    msg = f"prev consec_limit 须≥1，实得 {s.consec_limit}（symbol={s.symbol}）"
                    raise ValueError(msg)
            curr_height_by_symbol = {s.symbol: s.consec_limit for s in stocks}
            promotion_rates = {}
            for h in range(1, cfg.height_cap):
                base = [s for s in prev_stocks if s.consec_limit == h]
                if not base:
                    continue
                promoted = sum(
                    1 for s in base if curr_height_by_symbol.get(s.symbol) == h + 1
                )
                rate = promoted / len(base)
                promotion_rates[h] = rate
                if len(base) >= cfg.promotion_min_base and rate < cfg.promotion_warn_threshold:
                    warnings.append(
                        f"{h}进{h + 1}晋级率{rate * 100:.1f}%<{cfg.promotion_warn_threshold * 100:.0f}%"
                        f"断层预警（基数{len(base)}）"
                    )
        else:
            notes.append("无相邻昨日快照，晋级成功率腿降级")

        return LadderSnapshot(
            trade_date=trade_date,
            stock_count=len(stocks),
            max_height=max_height,
            height_distribution=distribution,
            fault_levels=faults,
            fault_severity=severity,
            seal_time_mean=seal_mean,
            seal_time_median=seal_median,
            early_seal_ratio=early_ratio,
            promotion_rates=promotion_rates,
            promotion_warnings=tuple(warnings),
            degraded=False,
            notes=tuple(notes),
        )

    # ── Granger 领导-跟随系数（leader→follower）─────────────────────
    def leadership(
        self,
        leader_returns: Sequence[float],
        follower_returns: Sequence[float],
        *,
        max_lag: int | None = None,
    ) -> LeadershipCoefficient:
        cfg = self._config
        lag = cfg.granger_max_lag if max_lag is None else int(max_lag)
        if lag < 1:
            msg = f"max_lag 须≥1，实得 {lag}"
            raise ValueError(msg)
        x = [float(v) for v in leader_returns]
        y = [float(v) for v in follower_returns]
        if len(x) != len(y):
            msg = f"leader 与 follower 不等长: {len(x)} vs {len(y)}"
            raise ValueError(msg)
        n = len(x)
        if not all(math.isfinite(v) for v in x) or not all(math.isfinite(v) for v in y):
            msg = "收益序列含非有限值（NaN/inf）"
            raise ValueError(msg)
        if n < cfg.granger_min_samples:
            return LeadershipCoefficient(
                checked=False,
                f_stat=None,
                p_value=None,
                leadership=None,
                is_leader=False,
                best_lag=None,
                n_samples=n,
                direction="none",
                notes=(f"样本 {n}<{cfg.granger_min_samples}，Granger 检验显式降级不阻断",),
            )

        t = n - lag
        yv = y[lag:]
        ylags = [y[lag - k : n - k] for k in range(1, lag + 1)]
        xlags = [x[lag - k : n - k] for k in range(1, lag + 1)]
        design_r = [[1.0] + [ylags[k][i] for k in range(lag)] for i in range(t)]
        design_u = [
            [1.0] + [ylags[k][i] for k in range(lag)] + [xlags[k][i] for k in range(lag)]
            for i in range(t)
        ]
        try:
            _, rss_r = _ols_solve(design_r, yv)
            beta_u, rss_u = _ols_solve(design_u, yv)
        except ValueError:
            return LeadershipCoefficient(
                checked=True,
                f_stat=0.0,
                p_value=1.0,
                leadership=0.0,
                is_leader=False,
                best_lag=None,
                n_samples=n,
                direction="none",
                notes=("设计矩阵奇异（常数列/完全共线），退化为不显著",),
            )

        df2 = t - (2 * lag + 1)
        x_betas = beta_u[1 + lag :]
        leadership_coef = sum(abs(b) for b in x_betas)
        if rss_r <= _RSS_EPS and rss_u <= _RSS_EPS:
            f_stat, pvalue = 0.0, 1.0  # y 零方差，无可解释变异
        elif rss_u <= _RSS_EPS:
            f_stat, pvalue = math.inf, 0.0
        else:
            f_stat = max(((rss_r - rss_u) / lag) / (rss_u / df2), 0.0)
            pvalue = _f_sf(f_stat, lag, df2) if math.isfinite(f_stat) else 0.0

        significant = pvalue < cfg.granger_significance
        is_leader = significant and leadership_coef > cfg.granger_threshold
        best_lag = max(range(lag), key=lambda k: abs(x_betas[k])) + 1 if significant else None
        return LeadershipCoefficient(
            checked=True,
            f_stat=float(f_stat),
            p_value=float(pvalue),
            leadership=float(leadership_coef),
            is_leader=is_leader,
            best_lag=best_lag,
            n_samples=n,
            direction="leader" if is_leader else "none",
            notes=(),
        )
