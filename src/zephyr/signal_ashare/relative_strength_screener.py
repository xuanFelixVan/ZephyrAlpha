# [BLUEPRINT] MOD-SIG-096 | docs/03_modules/_domain_signal/relative_strength_screener/blueprint.md
# [MODULE] zephyr.signal_ashare.relative_strength_screener
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas（基准指数序列由 D_DATA 注入；精筛选配按鸭子类型消费输出，零 import）
# [CONSUMERS] （候选：MOD-SIG-048 fine_scoring_engine 精筛选配层、选股漏斗）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 四维子分∈[0,100]；合成权重和=1；52周新高接近度=n期末收盘/52周最高高价；near_high_52w 阈值默认 0.95；放量突破=收盘创前52周新高且量≥1.5×20日均量；历史不足 252 根→degraded=True 显式降级；frozen dataclass asdict JSON 可序列化；不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01365 行 + 候选注册表 CAND-TESTB-011
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列/不等长/非正价格/非有限值/非法配置（权重和≠1 等） → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_relative_strength_screener.py
# [A_module] module_id=MOD-SIG-096 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""多维度相对强弱筛选（MOD-SIG-096，B10-01365）。

短线强度引擎+IC 加权校准已有（MOD-SIG-034 quant_short_term_strength_engine，
短线六维）；52 周新高接近度+新高放量突破确认为缺口（深挖裁定理由）。本模块
落地 O'Neil RS 评级口径的多维相对强弱合成评分（0-100）：

    合成分 = 区间RS 40% + 结构强弱 25% + 52周接近度 20% + 放量突破 15%

- **区间 RS**：20/60/120 日个股收益−基准收益加权超额（默认 0.5/0.3/0.2），
  映射 clip(50+超额×rs_scale, 0, 100)。
- **结构强弱**：close>MA20>MA50>MA120 多头排列四条件各 25 分。
- **52 周新高接近度**：close/max(high,252)，≥0.95 置 near_high_52w；
  子分=clip((接近度−0.8)/0.2,0,1)×100。
- **放量突破确认**：收盘创前 52 周新高且量≥1.5×20 日均量→confirmed/100 分；
  新高无量→40 分部分；无新高→0 分。

与既有件边界（查重裁定）：
- MOD-SIG-034 quant_short_term_strength_engine：短线六维评分（其 RS 维=
  个股涨幅−大盘涨幅短线口径），本件为中长期多维 RS+新高突破结构，正交互补。
- strength_ic_weight_calibrator：IC 权重校准件，不覆盖 52 周新高维度。
- MOD-SIG-048 fine_scoring_engine：精筛消费方候选（鸭子类型接入留集成批）。

依据: AUD-DRAFT-001 深挖批 B10-01365（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-096
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 个股 close/high/volume 序列 + 基准 close 序列（D_DATA 注入）
# 特征: 区间超额收益 / 均线多头条件 / 52周接近度 / 突破量比
# 算法: 四维子分（各 0-100）→ 权重合成 → 批量降序 rank
# 输出: RelativeStrengthScore（子分+接近度+确认标记+合成+degraded）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any, Final

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

__all__: Final = [
    "RelativeStrengthConfig",
    "RelativeStrengthScreener",
    "RelativeStrengthScore",
]

_WEIGHT_TOLERANCE: Final = 1e-6


@dataclass(frozen=True)
class RelativeStrengthConfig:
    """评分参数（构造即校验，fail-closed）。"""

    interval_windows: tuple[int, ...] = (20, 60, 120)
    interval_weights: tuple[float, ...] = (0.5, 0.3, 0.2)
    rs_scale: float = 200.0
    weight_interval_rs: float = 0.40
    weight_structural: float = 0.25
    weight_proximity: float = 0.20
    weight_breakout: float = 0.15
    near_high_threshold: float = 0.95
    proximity_floor: float = 0.80
    breakout_volume_multiple: float = 1.5
    volume_ma_window: int = 20
    year_bars: int = 252

    def __post_init__(self) -> None:
        if len(self.interval_windows) != len(self.interval_weights):
            msg = (
                f"interval_windows 与 interval_weights 不等长: "
                f"{len(self.interval_windows)} vs {len(self.interval_weights)}"
            )
            raise ValueError(msg)
        if any(w < 1 for w in self.interval_windows):
            msg = f"interval_windows 须全≥1: {self.interval_windows}"
            raise ValueError(msg)
        if abs(sum(self.interval_weights) - 1.0) > _WEIGHT_TOLERANCE:
            msg = f"interval_weights 和须=1，实得 {sum(self.interval_weights)}"
            raise ValueError(msg)
        total = (
            self.weight_interval_rs
            + self.weight_structural
            + self.weight_proximity
            + self.weight_breakout
        )
        if abs(total - 1.0) > _WEIGHT_TOLERANCE:
            msg = f"四维合成权重和须=1，实得 {total}"
            raise ValueError(msg)
        if self.rs_scale <= 0.0:
            msg = f"rs_scale 须>0，实得 {self.rs_scale}"
            raise ValueError(msg)
        if not (0.0 < self.near_high_threshold <= 1.0):
            msg = f"near_high_threshold 须∈(0,1]，实得 {self.near_high_threshold}"
            raise ValueError(msg)
        if not (0.0 <= self.proximity_floor < self.near_high_threshold):
            msg = f"proximity_floor 须∈[0,{self.near_high_threshold})，实得 {self.proximity_floor}"
            raise ValueError(msg)
        if self.breakout_volume_multiple < 1.0:
            msg = f"breakout_volume_multiple 须≥1，实得 {self.breakout_volume_multiple}"
            raise ValueError(msg)
        if self.volume_ma_window < 1:
            msg = f"volume_ma_window 须≥1，实得 {self.volume_ma_window}"
            raise ValueError(msg)
        if self.year_bars < 30:
            msg = f"year_bars 须≥30，实得 {self.year_bars}"
            raise ValueError(msg)


@dataclass(frozen=True)
class RelativeStrengthScore:
    """单标的多维 RS 评分输出。"""

    symbol: str
    rs_interval_score: float
    structural_score: float
    high_52w_proximity: float
    near_high_52w: bool
    breakout_confirmed: bool
    breakout_score: float
    composite_score: float
    degraded: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RelativeStrengthScreener:
    """多维度相对强弱筛选器（四维合成，纯函数核）。"""

    def __init__(self, config: RelativeStrengthConfig | None = None) -> None:
        self._config = config if config is not None else RelativeStrengthConfig()

    @property
    def config(self) -> RelativeStrengthConfig:
        return self._config

    def score(
        self,
        symbol: str,
        close: pd.Series,
        high: pd.Series,
        volume: pd.Series,
        benchmark_close: pd.Series,
    ) -> RelativeStrengthScore:
        """单标的多维 RS 评分（PIT：仅用序列末端及历史窗口）。"""
        cfg = self._config
        c = np.asarray(close, dtype=float)
        h = np.asarray(high, dtype=float)
        v = np.asarray(volume, dtype=float)
        b = np.asarray(benchmark_close, dtype=float)
        if c.size == 0:
            msg = "close 为空序列"
            raise ValueError(msg)
        if not (len(c) == len(h) == len(v) == len(b)):
            msg = (
                f"close/high/volume/benchmark 不等长: "
                f"{len(c)}/{len(h)}/{len(v)}/{len(b)}"
            )
            raise ValueError(msg)
        if not (np.isfinite(c).all() and np.isfinite(h).all()
                and np.isfinite(v).all() and np.isfinite(b).all()):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if (c <= 0).any() or (h <= 0).any() or (b <= 0).any():
            msg = "价格序列含非正值"
            raise ValueError(msg)
        if (v < 0).any():
            msg = "volume 含负值"
            raise ValueError(msg)

        n = len(c)
        degraded = n < cfg.year_bars

        # ── 区间 RS（加权超额收益 → 0-100）─────────────────────────
        excess = 0.0
        for w, wt in zip(cfg.interval_windows, cfg.interval_weights):
            k = min(w, n - 1)
            stock_ret = c[-1] / c[-1 - k] - 1.0
            bench_ret = b[-1] / b[-1 - k] - 1.0
            excess += wt * (stock_ret - bench_ret)
        rs_interval_score = float(np.clip(50.0 + excess * cfg.rs_scale, 0.0, 100.0))

        # ── 结构强弱（多头排列四条件）───────────────────────────────
        ma20 = float(c[-min(20, n) :].mean())
        ma50 = float(c[-min(50, n) :].mean())
        ma120 = float(c[-min(120, n) :].mean())
        conditions = (
            c[-1] > ma20,
            ma20 > ma50,
            ma50 > ma120,
            c[-1] > ma120,
        )
        structural_score = 25.0 * sum(conditions)

        # ── 52 周新高接近度 ────────────────────────────────────────
        window = min(cfg.year_bars, n)
        high_52w = float(h[-window:].max())
        proximity = float(c[-1] / high_52w)
        near_high = proximity >= cfg.near_high_threshold
        span = 1.0 - cfg.proximity_floor
        proximity_score = float(
            np.clip((proximity - cfg.proximity_floor) / span, 0.0, 1.0) * 100.0
        )

        # ── 放量突破确认 ───────────────────────────────────────────
        if n >= 2:
            prior_high = float(h[:-1][-min(cfg.year_bars, n - 1) :].max())
            is_new_high = bool(c[-1] > prior_high)
        else:
            is_new_high = False
        vol_window = min(cfg.volume_ma_window, n - 1)
        vol_ma = float(v[-1 - vol_window : -1].mean()) if vol_window >= 1 else 0.0
        volume_ratio = float(v[-1] / vol_ma) if vol_ma > 0.0 else 0.0
        confirmed = is_new_high and volume_ratio >= cfg.breakout_volume_multiple
        if confirmed:
            breakout_score = 100.0
        elif is_new_high:
            breakout_score = 40.0  # 新高无量：部分分（不确认）
        else:
            breakout_score = 0.0

        composite = (
            cfg.weight_interval_rs * rs_interval_score
            + cfg.weight_structural * structural_score
            + cfg.weight_proximity * proximity_score
            + cfg.weight_breakout * breakout_score
        )
        return RelativeStrengthScore(
            symbol=symbol,
            rs_interval_score=rs_interval_score,
            structural_score=structural_score,
            high_52w_proximity=proximity,
            near_high_52w=near_high,
            breakout_confirmed=confirmed,
            breakout_score=breakout_score,
            composite_score=float(np.clip(composite, 0.0, 100.0)),
            degraded=degraded,
        )

    def rank(
        self,
        bars: dict[str, tuple[pd.Series, pd.Series, pd.Series]],
        benchmark_close: pd.Series,
    ) -> list[RelativeStrengthScore]:
        """批量评分并按合成分降序（精筛选配接入位）。"""
        scored = [
            self.score(symbol, close, high, volume, benchmark_close)
            for symbol, (close, high, volume) in bars.items()
        ]
        return sorted(scored, key=lambda s: s.composite_score, reverse=True)
