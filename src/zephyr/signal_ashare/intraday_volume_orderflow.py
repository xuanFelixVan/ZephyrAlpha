# [BLUEPRINT] MOD-SIG-093 | docs/03_modules/_domain_signal/intraday_volume_orderflow/blueprint.md
# [MODULE] zephyr.signal_ashare.intraday_volume_orderflow
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas（分钟K/tick 由 D_DATA tick_subscriber/tick_redis_cache 上游注入，本模块不 import 数据链路）
# [CONSUMERS] （候选：MOD-SIG-094 Wyckoff 吸筹买点 CVD 确认、MOD-SIG-095 背离检测 CVD 腿、精筛装配层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] Volume Profile VA 覆盖率≥配置阈值（默认70%）；va_low≤POC≤va_high；CVD=Σsign(close−open)×volume 严格 PIT；背离方向封闭集（bullish/bearish）且 magnitude>0；VPIN∈[0,1]、50 桶默认、bucket<window→degraded；frozen dataclass asdict JSON 可序列化；纯函数不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01361 行 + 候选注册表 CAND-TESTB-008
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺列/空表/负量/非法 n_bins/非法桶参/总量为零 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_intraday_volume_orderflow.py
# [A_module] module_id=MOD-SIG-093 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""日内量能结构与订单流分析（MOD-SIG-093，B10-01361）。

日内连续竞价（9:30–15:00）量能三件套，纯函数核对注入的分钟K数据计算：

- **Volume Profile**：典型价 (H+L+C)/3 分桶聚合，POC（控制点=最大量能价位）+
  VA70%（价值区，自 POC 向量能大侧扩展至覆盖≥70%）。
- **CVD 背离追踪**：delta=sign(close−open)×volume 累加（BVC 简化口径，无买卖
  方向 tick 时的标准近似）；峰谷对位检测价新高/新低与 CVD 不配合的顶/底背离，
  magnitude=价格腿幅度−CVD 腿幅度（归一化到窗口量能）量化背离程度。
- **VPIN**：Easley-O'Hara 知情交易度量——等量 50 桶（默认）聚合 |净 delta|/桶量，
  尾窗均值输出日频值；桶数不足 window → degraded=True 不静默。

与既有件边界（查重裁定）：
- MOD-SIG-089 auction_microstructure_analyzer：**盘前竞价**（9:15–9:25 七族特征），
  本件为**日内连续竞价**量能结构，时段与口径正交（查重纪律④分工）。
- intelligence/event_score.py 内嵌 CVD 助手：PEAD 卖压吸收专用局部计算，
  非可复用信号件，不收编。
- 上游 D_DATA tick_subscriber/tick_redis_cache：数据链路注入位（蓝图 §3），
  本模块保持纯函数零 import 边（与 MOD-SIG-089 同构），生产接线留集成批。

依据: AUD-DRAFT-001 深挖批 B10-01361（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-093
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 分钟K DataFrame[open,high,low,close,volume]（D_DATA 注入）
# 特征: 典型价分桶量能 / bar delta 符号 / 等量桶净 delta
# 算法: VP 分桶+VA 扩展；CVD 累加+峰谷对位背离；VPIN 等量桶切分（跨桶比例拆分）
# 输出: VolumeProfile / CvdDivergence 列表 / VpinResult（日频）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any, Final

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

__all__: Final = [
    "CvdDivergence",
    "IntradayOrderflowConfig",
    "IntradayVolumeOrderflowAnalyzer",
    "VolumeProfile",
    "VpinResult",
    "IntradayVolumeOrderflow",  # scaffold 注册别名（__init__ export 契约）
]

_BAR_COLUMNS: Final = ("open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class IntradayOrderflowConfig:
    """计算参数（构造即校验，fail-closed）。"""

    n_bins: int = 30
    value_area_fraction: float = 0.70
    divergence_lookback: int = 5
    vpin_buckets: int = 50
    vpin_window: int = 50

    def __post_init__(self) -> None:
        if self.n_bins < 2:
            msg = f"n_bins 须≥2，实得 {self.n_bins}"
            raise ValueError(msg)
        if not (0.0 < self.value_area_fraction <= 1.0):
            msg = f"value_area_fraction 须∈(0,1]，实得 {self.value_area_fraction}"
            raise ValueError(msg)
        if self.divergence_lookback < 1:
            msg = f"divergence_lookback 须≥1，实得 {self.divergence_lookback}"
            raise ValueError(msg)
        if self.vpin_buckets < 1:
            msg = f"vpin_buckets 须≥1，实得 {self.vpin_buckets}"
            raise ValueError(msg)
        if self.vpin_window < 1:
            msg = f"vpin_window 须≥1，实得 {self.vpin_window}"
            raise ValueError(msg)


@dataclass(frozen=True)
class VolumeProfile:
    """量能分布输出。"""

    poc_price: float
    value_area_high: float
    value_area_low: float
    total_volume: float
    bin_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CvdDivergence:
    """CVD 背离事件（峰谷对位）。"""

    direction: str  # bullish / bearish（封闭集）
    bar_index: int
    price_value: float
    cvd_value: float
    magnitude: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VpinResult:
    """VPIN 日频输出。"""

    vpin: float
    bucket_count: int
    bucket_volume: float
    degraded: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_bars(bars: pd.DataFrame) -> None:
    missing = [c for c in _BAR_COLUMNS if c not in bars.columns]
    if missing:
        msg = f"bars 缺列: {missing}（须含 {list(_BAR_COLUMNS)}）"
        raise ValueError(msg)
    if bars.empty:
        msg = "bars 为空表"
        raise ValueError(msg)
    if (bars["volume"] < 0).any():
        msg = "volume 含负值"
        raise ValueError(msg)


class IntradayVolumeOrderflowAnalyzer:
    """日内量能结构三件套门面（纯函数核，无状态）。"""

    def __init__(self, config: IntradayOrderflowConfig | None = None) -> None:
        self._config = config if config is not None else IntradayOrderflowConfig()

    @property
    def config(self) -> IntradayOrderflowConfig:
        return self._config

    # ── Volume Profile ──────────────────────────────────────────────
    def volume_profile(self, bars: pd.DataFrame, n_bins: int | None = None) -> VolumeProfile:
        """分钟K 聚合量能分布：POC + VA（默认 70%）。"""
        _require_bars(bars)
        bins_n = self._config.n_bins if n_bins is None else int(n_bins)
        if bins_n < 2:
            msg = f"n_bins 须≥2，实得 {bins_n}"
            raise ValueError(msg)

        typical = (bars["high"] + bars["low"] + bars["close"]) / 3.0
        volume = bars["volume"].to_numpy(dtype=float)
        lo = float(bars["low"].min())
        hi = float(bars["high"].max())
        total = float(volume.sum())
        if hi <= lo:
            return VolumeProfile(
                poc_price=lo,
                value_area_high=hi,
                value_area_low=lo,
                total_volume=total,
                bin_count=bins_n,
            )

        edges = np.linspace(lo, hi, bins_n + 1)
        idx = np.clip(np.digitize(typical.to_numpy(dtype=float), edges[1:-1]), 0, bins_n - 1)
        bin_volume = np.zeros(bins_n)
        np.add.at(bin_volume, idx, volume)

        poc_idx = int(np.argmax(bin_volume))
        poc_price = float((edges[poc_idx] + edges[poc_idx + 1]) / 2.0)

        target = self._config.value_area_fraction * total
        covered = float(bin_volume[poc_idx])
        lo_idx = hi_idx = poc_idx
        while covered < target and (lo_idx > 0 or hi_idx < bins_n - 1):
            up_vol = bin_volume[hi_idx + 1] if hi_idx < bins_n - 1 else -1.0
            down_vol = bin_volume[lo_idx - 1] if lo_idx > 0 else -1.0
            if up_vol >= down_vol:
                hi_idx += 1
                covered += float(bin_volume[hi_idx])
            else:
                lo_idx -= 1
                covered += float(bin_volume[lo_idx])
        return VolumeProfile(
            poc_price=poc_price,
            value_area_high=float(edges[hi_idx + 1]),
            value_area_low=float(edges[lo_idx]),
            total_volume=total,
            bin_count=bins_n,
        )

    # ── CVD ─────────────────────────────────────────────────────────
    def cvd(self, bars: pd.DataFrame) -> pd.Series:
        """累积量差：Σ sign(close−open)×volume（BVC 简化口径，PIT 严格）。"""
        _require_bars(bars)
        delta = np.sign(bars["close"] - bars["open"]) * bars["volume"]
        return delta.cumsum()

    def cvd_divergences(
        self, bars: pd.DataFrame, lookback: int | None = None
    ) -> list[CvdDivergence]:
        """峰谷对位背离：价新高 CVD 不配合→bearish；价新低 CVD 抬升→bullish。

        magnitude = |价格腿| + |CVD 逆向腿|（CVD 腿归一化到窗口量能），恒>0。
        """
        _require_bars(bars)
        lb = self._config.divergence_lookback if lookback is None else int(lookback)
        if lb < 1:
            msg = f"lookback 须≥1，实得 {lb}"
            raise ValueError(msg)

        close = bars["close"].to_numpy(dtype=float)
        volume = bars["volume"].to_numpy(dtype=float)
        cvd = self.cvd(bars).to_numpy(dtype=float)
        events: list[CvdDivergence] = []
        for i in range(lb, len(bars)):
            window = close[i - lb : i]
            # 顶背离：价创窗口新高，CVD 不创新高
            k = i - lb + int(np.argmax(window))
            if close[i] > close[k] and cvd[i] <= cvd[k]:
                wv = float(volume[k + 1 : i + 1].sum())
                if wv > 0.0:
                    price_leg = close[i] / close[k] - 1.0
                    cvd_leg = (cvd[i] - cvd[k]) / wv
                    events.append(
                        CvdDivergence(
                            direction="bearish",
                            bar_index=i,
                            price_value=float(close[i]),
                            cvd_value=float(cvd[i]),
                            magnitude=float(price_leg - cvd_leg),
                        )
                    )
            # 底背离：价创窗口新低，CVD 不创新低
            k2 = i - lb + int(np.argmin(window))
            if close[i] < close[k2] and cvd[i] >= cvd[k2]:
                wv = float(volume[k2 + 1 : i + 1].sum())
                if wv > 0.0:
                    price_leg = close[i] / close[k2] - 1.0
                    cvd_leg = (cvd[i] - cvd[k2]) / wv
                    events.append(
                        CvdDivergence(
                            direction="bullish",
                            bar_index=i,
                            price_value=float(close[i]),
                            cvd_value=float(cvd[i]),
                            magnitude=float(cvd_leg - price_leg),
                        )
                    )
        return events

    # ── VPIN ────────────────────────────────────────────────────────
    def vpin(
        self,
        bars: pd.DataFrame,
        n_buckets: int | None = None,
        window: int | None = None,
    ) -> VpinResult:
        """VPIN 日频输出：等量桶 |净 delta|/桶量 的尾窗均值（Easley-O'Hara）。

        跨桶 bar 按量比例拆分 delta；桶数不足 window → degraded=True。
        """
        _require_bars(bars)
        buckets = self._config.vpin_buckets if n_buckets is None else int(n_buckets)
        win = self._config.vpin_window if window is None else int(window)
        if buckets < 1:
            msg = f"n_buckets 须≥1，实得 {buckets}"
            raise ValueError(msg)
        if win < 1:
            msg = f"window 须≥1，实得 {win}"
            raise ValueError(msg)

        volume = bars["volume"].to_numpy(dtype=float)
        delta = (np.sign(bars["close"] - bars["open"]) * bars["volume"]).to_numpy(dtype=float)
        total = float(volume.sum())
        if total <= 0.0:
            msg = "volume 总量为零，无法聚合等量桶"
            raise ValueError(msg)
        bucket_volume = total / buckets

        imbalances: list[float] = []
        acc_vol = 0.0
        acc_delta = 0.0
        for v, d in zip(volume, delta):
            remaining = float(v)
            while remaining > 0.0:
                take = min(bucket_volume - acc_vol, remaining)
                acc_delta += float(d) * (take / float(v)) if v > 0.0 else 0.0
                acc_vol += take
                remaining -= take
                if bucket_volume - acc_vol <= 1e-9:
                    imbalances.append(abs(acc_delta))
                    acc_vol = 0.0
                    acc_delta = 0.0
        if not imbalances:
            msg = "数据不足以聚合出完整等量桶"
            raise ValueError(msg)

        bucket_count = len(imbalances)
        degraded = bucket_count < win
        use = imbalances if degraded else imbalances[-win:]
        vpin_value = float(np.mean(use) / bucket_volume)
        return VpinResult(
            vpin=min(max(vpin_value, 0.0), 1.0),
            bucket_count=bucket_count,
            bucket_volume=bucket_volume,
            degraded=degraded,
        )


# scaffold 注册别名（__init__.py export 契约）
IntradayVolumeOrderflow = IntradayVolumeOrderflowAnalyzer
