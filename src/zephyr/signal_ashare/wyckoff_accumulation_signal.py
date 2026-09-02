# [BLUEPRINT] MOD-SIG-094 | docs/03_modules/_domain_signal/wyckoff_accumulation_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.wyckoff_accumulation_signal
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas（wyckoff 阶段评分由 MOD-REGIME-002 注入、CVD 由 MOD-SIG-093 契约注入，鸭子类型零 import——域方向 regime→signal_ashare 纪律）
# [CONSUMERS] （候选：买入侧装配层、MOD-SIG-086 漏斗骨架）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 买点=评分上穿门槛+CVD 窗口上行双确认；置信度=评分/100∈(0,1]；Granger 防倒置=ΔCVD 领先 Δ评分 显著才放行（倒置全阻断）；样本不足→granger_checked=False 显式降级不阻断；F 检验 p 值由纯 Python 不完全贝塔实现（无 scipy 幽灵依赖）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01362 行 + 候选注册表 CAND-TESTB-009
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不等长/过短/NaN/评分越界[0,100]/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_wyckoff_accumulation_signal.py
# [A_module] module_id=MOD-SIG-094 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""Wyckoff 吸筹买点信号（MOD-SIG-094，B10-01362）。

吸筹六阶段 FSM+评分已有（MOD-REGIME-002 wyckoff_engine，score∈[0,100]）；
信号化买入确认（CVD）+Granger 因果自检为缺口（深挖裁定理由）。本模块消费
wyckoff 阶段评分（鸭子类型注入，守域方向 regime→signal_ashare 纪律），叠加
CVD 确认生成吸筹买点：

    买点 = 评分上穿门槛（默认 60，对齐 S2 confirm 门槛）+ CVD 窗口上行确认

- **CVD 确认**：上穿点 CVD 高于 cvd_rise_window 根前（买方压力积累），否则
  候选拒绝（吸筹无量能配合=可疑）。
- **Granger 防倒置**：对 ΔCVD→Δ评分 做滞后 OLS F 检验——意图方向（买方压力
  领先评分抬升）显著才放行；不显著（含评分领先量差的倒置情形）→ 候选全阻断。
  样本不足 granger_min_obs → checked=False 显式降级不阻断（不静默）。
- **零 scipy 依赖**：F 分布右尾 p 值以纯 Python 正则化不完全贝塔（连分式）
  实现（pyproject 幽灵依赖纪律，scipy 未声明）。

与既有件边界（查重裁定）：
- MOD-REGIME-002 wyckoff_engine：阶段识别+评分生产方（本件消费其输出，不重写）。
- MOD-SIG-093 intraday_volume_orderflow：CVD 序列生产契约（注入消费）。
- sentiment_cycle 顶背离/t0_point_analyzer 日内量价背离：语义不同（情绪/做T），正交。

依据: AUD-DRAFT-001 深挖批 B10-01362（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-094
Version: 0.1.0

# [ALGO_FLOW]
# 输入: wyckoff_score 序列（MOD-REGIME-002 注入）+ cvd 序列（MOD-SIG-093 契约注入）
# 特征: 评分上穿事件 + CVD 窗口斜率 + Δ序列滞后相关结构
# 算法: 上穿检测 → CVD 确认过滤 → Granger F 检验（受限/非受限 OLS + 不完全贝塔 p 值）
# 输出: AccumulationResult（signals/candidate_count/granger 三态/blocked_by_granger）
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass
from typing import Any, Final

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

__all__: Final = [
    "AccumulationResult",
    "AccumulationSignal",
    "GrangerResult",
    "WyckoffAccumulationConfig",
    "WyckoffAccumulationSignal",
]

_TINY: Final = 1e-300
_BETACF_EPS: Final = 3e-14
_BETACF_MAX_ITER: Final = 200


@dataclass(frozen=True)
class WyckoffAccumulationConfig:
    """买点与因果自检参数（构造即校验，fail-closed）。"""

    score_threshold: float = 60.0  # 对齐 wyckoff_engine S2 confirm 门槛（Spring 后 60+）
    cvd_rise_window: int = 5
    granger_max_lag: int = 5
    granger_pvalue: float = 0.05
    granger_min_obs: int = 60

    def __post_init__(self) -> None:
        if not (0.0 < self.score_threshold <= 100.0):
            msg = f"score_threshold 须∈(0,100]，实得 {self.score_threshold}"
            raise ValueError(msg)
        if self.cvd_rise_window < 1:
            msg = f"cvd_rise_window 须≥1，实得 {self.cvd_rise_window}"
            raise ValueError(msg)
        if self.granger_max_lag < 1:
            msg = f"granger_max_lag 须≥1，实得 {self.granger_max_lag}"
            raise ValueError(msg)
        if not (0.0 < self.granger_pvalue < 1.0):
            msg = f"granger_pvalue 须∈(0,1)，实得 {self.granger_pvalue}"
            raise ValueError(msg)
        if self.granger_min_obs < 4 * self.granger_max_lag + 10:
            msg = f"granger_min_obs 须≥4×lag+10={4 * self.granger_max_lag + 10}，实得 {self.granger_min_obs}"
            raise ValueError(msg)


@dataclass(frozen=True)
class AccumulationSignal:
    """单条吸筹买点。"""

    bar_index: int
    wyckoff_score: float
    cvd_slope: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GrangerResult:
    """Granger F 检验输出（x→y 单方向）。"""

    f_stat: float
    pvalue: float
    lag: int
    significant: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccumulationResult:
    """买点批量输出 + Granger 三态。"""

    signals: tuple[AccumulationSignal, ...]
    candidate_count: int
    cvd_confirmed_count: int
    granger_checked: bool
    granger_passed: bool
    blocked_by_granger: int

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["signals"] = [s.to_dict() for s in self.signals]
        return d


# ── 纯 Python F 分布右尾（正则化不完全贝塔，Numerical Recipes 连分式）────────
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
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _f_sf(f_stat: float, d1: int, d2: int) -> float:
    """F 分布右尾 P(F>f) = I_{d2/(d2+d1·f)}(d2/2, d1/2)。"""
    if f_stat <= 0.0:
        return 1.0
    x = d2 / (d2 + d1 * f_stat)
    return _ibeta(d2 / 2.0, d1 / 2.0, x)


class WyckoffAccumulationSignal:
    """吸筹买点信号引擎（评分×CVD 双确认 + Granger 防倒置）。"""

    def __init__(self, config: WyckoffAccumulationConfig | None = None) -> None:
        self._config = config if config is not None else WyckoffAccumulationConfig()

    @property
    def config(self) -> WyckoffAccumulationConfig:
        return self._config

    # ── Granger 因果（x→y：滞后 OLS F 检验）──────────────────────────
    def granger_causality(self, x: pd.Series, y: pd.Series, max_lag: int | None = None) -> GrangerResult:
        """检验 x 是否 Granger 引起 y（受限=自身滞后 vs 非受限=自身+x 滞后）。"""
        lag = self._config.granger_max_lag if max_lag is None else int(max_lag)
        if lag < 1:
            msg = f"max_lag 须≥1，实得 {lag}"
            raise ValueError(msg)
        xa = np.asarray(x, dtype=float)
        ya = np.asarray(y, dtype=float)
        if len(xa) != len(ya):
            msg = f"x 与 y 不等长: {len(xa)} vs {len(ya)}"
            raise ValueError(msg)
        n = len(xa)
        if n <= 3 * lag + 1:
            msg = f"样本量 {n} 不足以支撑 lag={lag} 的 Granger 检验"
            raise ValueError(msg)
        if not (np.isfinite(xa).all() and np.isfinite(ya).all()):
            msg = "x/y 含非有限值"
            raise ValueError(msg)

        t = n - lag
        yv = ya[lag:]
        ylags = [ya[lag - k : n - k] for k in range(1, lag + 1)]
        xlags = [xa[lag - k : n - k] for k in range(1, lag + 1)]
        xr = np.column_stack([np.ones(t)] + ylags)
        xu = np.column_stack([np.ones(t)] + ylags + xlags)

        beta_r, *_ = np.linalg.lstsq(xr, yv, rcond=None)
        rss_r = float(np.sum((yv - xr @ beta_r) ** 2))
        beta_u, *_ = np.linalg.lstsq(xu, yv, rcond=None)
        rss_u = float(np.sum((yv - xu @ beta_u) ** 2))

        df2 = t - xu.shape[1]
        if rss_u <= 1e-12:
            f_stat = math.inf
            pvalue = 0.0
        else:
            f_stat = ((rss_r - rss_u) / lag) / (rss_u / df2)
            f_stat = max(f_stat, 0.0)
            pvalue = _f_sf(f_stat, lag, df2) if math.isfinite(f_stat) else 0.0
        return GrangerResult(
            f_stat=float(f_stat),
            pvalue=float(pvalue),
            lag=lag,
            significant=bool(pvalue < self._config.granger_pvalue),
        )

    # ── 买点生成 ────────────────────────────────────────────────────
    def generate(self, wyckoff_score: pd.Series, cvd: pd.Series) -> AccumulationResult:
        """评分上穿门槛 + CVD 确认 → 买点；Granger 倒置 → 全阻断。"""
        s = np.asarray(wyckoff_score, dtype=float)
        c = np.asarray(cvd, dtype=float)
        if len(s) != len(c):
            msg = f"wyckoff_score 与 cvd 不等长: {len(s)} vs {len(c)}"
            raise ValueError(msg)
        cfg = self._config
        if len(s) < cfg.cvd_rise_window + 2:
            msg = f"序列过短（{len(s)}<{cfg.cvd_rise_window + 2}）"
            raise ValueError(msg)
        if not (np.isfinite(s).all() and np.isfinite(c).all()):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if (s < 0.0).any() or (s > 100.0).any():
            msg = "wyckoff_score 越界 [0,100]"
            raise ValueError(msg)

        thr = cfg.score_threshold
        w = cfg.cvd_rise_window
        candidates = [i for i in range(1, len(s)) if s[i] >= thr and s[i - 1] < thr]
        confirmed: list[tuple[int, float]] = []
        for i in candidates:
            j = max(0, i - w)
            if c[i] > c[j]:
                confirmed.append((i, (c[i] - c[j]) / max(i - j, 1)))

        checked = len(s) >= cfg.granger_min_obs
        if checked:
            forward = self.granger_causality(pd.Series(np.diff(c)), pd.Series(np.diff(s)))
            passed = forward.significant
        else:
            passed = True  # 样本不足：显式降级不阻断（checked=False 落档）

        blocked = len(confirmed) if (checked and not passed) else 0
        signals: tuple[AccumulationSignal, ...] = ()
        if not blocked:
            signals = tuple(
                AccumulationSignal(
                    bar_index=i,
                    wyckoff_score=float(s[i]),
                    cvd_slope=float(slope),
                    confidence=float(s[i] / 100.0),
                )
                for i, slope in confirmed
            )
        return AccumulationResult(
            signals=signals,
            candidate_count=len(candidates),
            cvd_confirmed_count=len(confirmed),
            granger_checked=checked,
            granger_passed=passed,
            blocked_by_granger=blocked,
        )
