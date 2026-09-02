# [BLUEPRINT] MOD-SIG-101 | docs/03_modules/_domain_signal/sentiment_price_divergence/blueprint.md
# [MODULE] zephyr.signal_ashare.sentiment_price_divergence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；情绪指数与价格序列鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：情绪页背离告警、买入侧背离过滤装配层；上游情绪指数 MOD-SIG-025 market_sentiment_analyzer）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] SDI=ΔSentiment_z−ΔPrice_z（Δ=当前 z−lag 根前 z）；窗零方差 → z=0+notes 不伪造背离；方向三态封闭集（bullish/bearish/none，阈值双侧对称）；置信度=min(|SDI|/scale,1)∈[0,1]；scan 仅收 direction≠none 事件；PIT（z/Δ 全部滚动窗前视）；frozen dataclass asdict JSON 可序列化；纯统计核不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01371 行 + 候选注册表 CAND-TESTB-016
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 序列不等长/短于 z_window+delta_lag/非有限值/非正价格/配置越界 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_sentiment_price_divergence.py
# [A_module] module_id=MOD-SIG-101 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""情绪-价格背离指数模型（MOD-SIG-101，B10-01371，Sentiment-Price Divergence Index）。

场内对账（查重铁律⑤分工在案）：sector_divergence（MOD-SIG-060）= 板块间分歧度
（横截面）、multi_indicator_divergence（MOD-SIG-095）= RSI/MACD/CVD 技术指标峰谷
背离（价格-指标对位，语义正交裁定 P1W02 fragment 在案）；**情绪-价格 z 分差背离
SDI=ΔSentiment_z−ΔPrice_z 无实现**（深挖批 min_build_spec 明示，核心类
SentimentPriceDivergence），本模块落地。情绪指数由 MOD-SIG-025
market_sentiment_analyzer 产出注入（鸭子类型，不 import）。

口径：

- z 分差：z_s/z_p =（当前值 − 滚动窗均值）/窗总体标准差（默认窗 60）；
  窗零方差 → z=0 + notes（恒定窗无信息）。
- SDI = ΔSentiment_z − ΔPrice_z，Δ = 当前 z − lag 根前 z（默认 lag=5）。
- 方向：SDI≥+threshold（默认 1.0）→ bullish（情绪改善显著快于价格）；
  ≤−threshold → bearish；其间 → none。
- 置信度 = min(|SDI|/confidence_scale, 1)（scale 默认 2.0）。
- scan：自首个可算根逐根前视，仅收 direction≠none 背离事件（带 bar_index）。

依据: AUD-DRAFT-001 深挖批 B10-01371（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-101
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 情绪指数序列 + 价格序列（等长，尾部=最新）
# 特征: 滚动窗 z 分差 + lag 根差分
# 算法: z 计算（零方差降级）→ Δz 差分 → SDI → 方向/置信度判定 → scan 事件表
# 输出: DivergenceReading（SDI/双 Δz/双 z/方向/置信度/背离标记）
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "DivergenceReading",
    "SentimentPriceDivergence",
    "SentimentPriceDivergenceConfig",
]


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class SentimentPriceDivergenceConfig:
    """窗/滞后/阈值配置（构造即校验，fail-closed）。"""

    z_window: int = 60
    delta_lag: int = 5
    divergence_threshold: float = 1.0
    confidence_scale: float = 2.0

    def __post_init__(self) -> None:
        if self.z_window < 10:
            msg = f"z_window 须≥10，实得 {self.z_window}"
            raise ValueError(msg)
        if self.delta_lag < 1:
            msg = f"delta_lag 须≥1，实得 {self.delta_lag}"
            raise ValueError(msg)
        if self.divergence_threshold <= 0.0:
            msg = f"divergence_threshold 须>0，实得 {self.divergence_threshold}"
            raise ValueError(msg)
        if self.confidence_scale <= 0.0:
            msg = f"confidence_scale 须>0，实得 {self.confidence_scale}"
            raise ValueError(msg)


@dataclass(frozen=True)
class DivergenceReading:
    """SDI 单点读数。"""

    bar_index: int
    sdi: float
    delta_sentiment_z: float
    delta_price_z: float
    sentiment_z: float
    price_z: float
    direction: str
    divergence: bool
    confidence: float
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class SentimentPriceDivergence:
    """情绪-价格背离指数引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: SentimentPriceDivergenceConfig | None = None) -> None:
        self._config = config if config is not None else SentimentPriceDivergenceConfig()

    @property
    def config(self) -> SentimentPriceDivergenceConfig:
        return self._config

    # ── 输入校验 ──────────────────────────────────────────────────
    def _validate(self, sentiment: list[float], prices: list[float]) -> None:
        cfg = self._config
        if len(sentiment) != len(prices):
            msg = f"情绪与价格序列不等长: {len(sentiment)} vs {len(prices)}"
            raise ValueError(msg)
        min_len = cfg.z_window + cfg.delta_lag
        if len(sentiment) < min_len:
            msg = f"历史 {len(sentiment)}<z_window+delta_lag={min_len}"
            raise ValueError(msg)
        if not all(math.isfinite(v) for v in sentiment) or not all(math.isfinite(v) for v in prices):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if any(p <= 0.0 for p in prices):
            msg = "价格含非正值"
            raise ValueError(msg)

    # ── 单根 z（零方差 → 0.0 + 标记）───────────────────────────────
    def _z_at(self, series: Sequence[float], idx: int) -> tuple[float, bool]:
        w = self._config.z_window
        window = series[idx - w + 1 : idx + 1]
        sd = statistics.pstdev(window)
        if sd == 0.0:
            return 0.0, True
        return (series[idx] - statistics.fmean(window)) / sd, False

    def _reading_at(self, sentiment: Sequence[float], prices: Sequence[float], idx: int) -> DivergenceReading:
        cfg = self._config
        z_s, deg_s = self._z_at(sentiment, idx)
        z_p, deg_p = self._z_at(prices, idx)
        z_s_prev, _ = self._z_at(sentiment, idx - cfg.delta_lag)
        z_p_prev, _ = self._z_at(prices, idx - cfg.delta_lag)
        d_s = z_s - z_s_prev
        d_p = z_p - z_p_prev
        sdi = d_s - d_p
        if sdi >= cfg.divergence_threshold:
            direction = "bullish"
        elif sdi <= -cfg.divergence_threshold:
            direction = "bearish"
        else:
            direction = "none"
        notes: list[str] = []
        if deg_s:
            notes.append("情绪窗零方差，z_s 按 0 降级")
        if deg_p:
            notes.append("价格窗零方差，z_p 按 0 降级")
        return DivergenceReading(
            bar_index=idx,
            sdi=sdi,
            delta_sentiment_z=d_s,
            delta_price_z=d_p,
            sentiment_z=z_s,
            price_z=z_p,
            direction=direction,
            divergence=direction != "none",
            confidence=min(abs(sdi) / cfg.confidence_scale, 1.0),
            notes=tuple(notes),
        )

    # ── 最新读数 ──────────────────────────────────────────────────
    def compute(self, sentiment_scores: Sequence[float], prices: Sequence[float]) -> DivergenceReading:
        sentiment = [float(v) for v in sentiment_scores]
        price_list = [float(v) for v in prices]
        self._validate(sentiment, price_list)
        return self._reading_at(sentiment, price_list, len(sentiment) - 1)

    # ── 背离事件表（逐根前视）──────────────────────────────────────
    def scan(self, sentiment_scores: Sequence[float], prices: Sequence[float]) -> list[DivergenceReading]:
        sentiment = [float(v) for v in sentiment_scores]
        price_list = [float(v) for v in prices]
        self._validate(sentiment, price_list)
        cfg = self._config
        first = cfg.z_window - 1 + cfg.delta_lag
        return [
            r
            for r in (self._reading_at(sentiment, price_list, i) for i in range(first, len(sentiment)))
            if r.divergence
        ]
