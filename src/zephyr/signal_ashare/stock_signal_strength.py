# [BLUEPRINT] MOD-SIG-073 | 待统筹登记（缺口总账 GAP-F-39 行）
# [MODULE] zephyr.signal_ashare.stock_signal_strength
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy（纯函数核，零 DB/网络；AI NLP 维度由上游注入分数，本模块不调 LLM）
# [CONSUMERS] （候选：个股决策卡 / 猎杀矩阵式看板强度列，GAP-F-39 消费位；与 GAP-F-31 指数级共振评分同族个股级）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 五维封闭 {macd,rsi,volume,ma,ai_nlp}；各维分 ∈ [0,100]；合成=可用维加权均值（权重常量可配，负权重/全零权重 fail-closed）；AI NLP 缺省=剔除该维+权重重归一+notes 留痕；PIT（仅用注入序列末态）；纯函数确定性（同输入同输出）；frozen dataclass JSON 可序列化；强度分是状态描摹非点位预测（90号 §7）
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-39 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（根数不足/序列不等长/负价负量/ai_nlp_score 越界/权重非法，fail-closed）
# [TESTS] tests/signal_ashare/test_stock_signal_strength.py
# [A_module] module_id=MOD-SIG-073 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""个股级信号强度合成器（MOD-SIG-073，GAP-F-39）。

缺口总账 GAP-F-39（个股决策卡 / 猎杀矩阵式看板）：MACD/RSI/量能/均线/AI NLP
五维归一化到 [0,100] 后加权合成 0~100 强度分（权重常量可配，初拍值待实盘标定）。

五维口径（文档化初版映射，非校准概率）：

| 维 | 口径 | 映射 |
|---|---|---|
| MACD(12,26,9) | hist=(DIF-DEA)/close×100（价格无关化） | 100×sigmoid(k×hist_pct)，k=1 |
| RSI(14) | Wilder RSI | 直接取用（本已 0~100，50 中性） |
| 量能 | 5/20 日均量比 × 近 5 日价格方向 | 50+40×tanh(clip(量比-1,-0.5,2))×sign(ret5) |
| 均线(20) | close vs MA20 × MA20 斜率(5 日) | 50±25±25 四档 |
| AI NLP | 上游舆情情感分注入 [0,100] | 缺省=剔除+重归一 |

合成：strength=Σw·s/Σw（仅可用维），标签 强/偏强/中性/偏弱/弱（80/60/40/20）。

不做什么：不调 LLM（NLP 分注入）/不读库/不下单/不预测点位。

依据: 缺口总账 GAP-F-39（GAP-F-31 指数级同族）
SSoT: depgraph node 10505566（MOD-SIG-073，待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: closes/volumes 升序序列（等长 ≥min_bars）+ ai_nlp_score 可选注入 + StrengthConfig
# 特征: MACD hist/RSI/量比/均线位置+斜率/NLP 分
# 算法: 五维归一 [0,100] → 可用维加权合成 → 五档标签
# 输出: StrengthResult（strength 0~100 + 五维明细 + notes）
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

import numpy as np

logger = logging.getLogger(__name__)

__all__: Final = [
    "DIMENSION_KEYS",
    "DimensionScore",
    "StrengthConfig",
    "StrengthResult",
    "compose_strength",
]

#: 五维键（封闭集合，展示序）
DIMENSION_KEYS: Final[tuple[str, ...]] = ("macd", "rsi", "volume", "ma", "ai_nlp")

_DIM_NAME_ZH: Final[dict[str, str]] = {
    "macd": "MACD",
    "rsi": "RSI",
    "volume": "量能",
    "ma": "均线",
    "ai_nlp": "AI NLP",
}

_LABEL_BANDS: Final = ((80.0, "强"), (60.0, "偏强"), (40.0, "中性"), (20.0, "偏弱"))


@dataclass(frozen=True, slots=True)
class StrengthConfig:
    """五维合成配置（权重常量可配，初拍值待实盘标定；参数 >4 收 dataclass）。"""

    w_macd: float = 0.25
    w_rsi: float = 0.20
    w_volume: float = 0.20
    w_ma: float = 0.20
    w_ai_nlp: float = 0.15
    macd_sensitivity: float = 1.0  # hist_pct 每 1% 对应的 sigmoid 斜率
    rsi_period: int = 14
    ma_period: int = 20
    vol_short: int = 5
    vol_long: int = 20
    min_bars: int = 35  # MACD(26+9) 至少 34 根可用值，取 35 兜底

    def __post_init__(self) -> None:
        weights = (self.w_macd, self.w_rsi, self.w_volume, self.w_ma, self.w_ai_nlp)
        if any(float(w) < 0.0 for w in weights):
            raise ValueError(f"权重非法（须全部 ≥0）: {weights!r}")
        if sum(float(w) for w in weights) <= 0.0:
            raise ValueError("权重非法（全零无权合成）")
        if float(self.macd_sensitivity) <= 0.0:
            raise ValueError(f"macd_sensitivity 非法（须 >0）: {self.macd_sensitivity!r}")
        for name in ("rsi_period", "ma_period", "vol_short", "vol_long"):
            if int(getattr(self, name)) < 2:
                raise ValueError(f"{name} 非法（须 ≥2）: {getattr(self, name)!r}")
        if int(self.min_bars) < 35:
            raise ValueError(f"min_bars 非法（MACD 26+9 口径须 ≥35）: {self.min_bars!r}")

    def weight_of(self, key: str) -> float:
        return float(
            {
                "macd": self.w_macd,
                "rsi": self.w_rsi,
                "volume": self.w_volume,
                "ma": self.w_ma,
                "ai_nlp": self.w_ai_nlp,
            }[key]
        )


@dataclass(frozen=True, slots=True)
class DimensionScore:
    """单维强度分（0~100 + 理由留痕）。"""

    key: str
    name_zh: str
    score: float
    available: bool = True
    detail: str = ""


@dataclass(frozen=True, slots=True)
class StrengthResult:
    """五维合成产出（JSON 可序列化）。"""

    strength: float  # 0~100 合成强度
    label: str  # 强/偏强/中性/偏弱/弱
    dimensions: tuple[DimensionScore, ...]
    ai_nlp_included: bool
    config: StrengthConfig
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── 指标核（纯函数）──


def _ema(arr: np.ndarray, period: int) -> np.ndarray:
    k = 2.0 / (period + 1.0)
    out = np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = arr[i] * k + out[i - 1] * (1.0 - k)
    return out


def _score_macd(closes: np.ndarray, cfg: StrengthConfig) -> tuple[float, str]:
    dif = _ema(closes, 12) - _ema(closes, 26)
    dea = _ema(dif, 9)
    hist = float(dif[-1] - dea[-1])
    hist_pct = hist / float(closes[-1]) * 100.0  # 价格无关化（%）
    score = 100.0 / (1.0 + math.exp(-cfg.macd_sensitivity * hist_pct))
    return score, f"hist_pct={hist_pct:+.3f}%"


def _score_rsi(closes: np.ndarray, cfg: StrengthConfig) -> tuple[float, str]:
    period = cfg.rsi_period
    diff = np.diff(closes)
    gains = np.maximum(diff, 0.0)
    losses = np.maximum(-diff, 0.0)
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))
    for i in range(period, len(diff)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0.0:
        rsi = 100.0 if avg_gain > 0.0 else 50.0
    else:
        rsi = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    return min(max(rsi, 0.0), 100.0), f"RSI{period}={rsi:.1f}"


def _score_volume(closes: np.ndarray, volumes: np.ndarray, cfg: StrengthConfig) -> tuple[float, str]:
    ratio = float(np.mean(volumes[-cfg.vol_short :]) / np.mean(volumes[-cfg.vol_long :]))
    ret5 = float(closes[-1] / closes[-6] - 1.0)
    if ret5 == 0.0:
        return 50.0, f"量比={ratio:.2f} 价格走平"
    excess = min(max(ratio - 1.0, -0.5), 2.0)
    score = 50.0 + 40.0 * math.tanh(excess) * (1.0 if ret5 > 0 else -1.0)
    return score, f"量比={ratio:.2f} ret5={ret5:+.2%}"


def _score_ma(closes: np.ndarray, cfg: StrengthConfig) -> tuple[float, str]:
    p = cfg.ma_period
    ma_now = float(np.mean(closes[-p:]))
    ma_prev = float(np.mean(closes[-p - 5 : -5]))
    above = float(closes[-1]) > ma_now
    rising = ma_now > ma_prev
    score = 50.0 + (25.0 if above else -25.0) + (25.0 if rising else -25.0)
    return score, f"close{'>' if above else '<='}MA{p} MA斜率{'升' if rising else '降'}"


def _label_of(strength: float) -> str:
    for floor, label in _LABEL_BANDS:
        if strength >= floor:
            return label
    return "弱"


def compose_strength(
    closes: Sequence[float],
    volumes: Sequence[float],
    *,
    ai_nlp_score: float | None = None,
    config: StrengthConfig | None = None,
) -> StrengthResult:
    """五维信号强度合成主入口（0~100 + 各维明细）。

    Args:
        closes: 收盘价升序序列（正且有限，≥min_bars 根）。
        volumes: 成交量升序序列（≥0，与 closes 等长）。
        ai_nlp_score: 上游 AI NLP 情感分 [0,100]；None=剔除该维并重归一。
        config: 合成配置（None=设计默认值）。

    Returns:
        StrengthResult（strength 0~100 + label + 五维明细）。

    Raises:
        ValueError: 输入/权重非法（fail-closed）。
    """
    cfg = config or StrengthConfig()
    c = np.asarray(list(closes), dtype=float)
    v = np.asarray(list(volumes), dtype=float)
    if len(c) != len(v):
        raise ValueError(f"收盘价与成交量序列须等长: {len(c)} vs {len(v)}")
    if len(c) < cfg.min_bars:
        raise ValueError(f"根数不足（须 ≥{cfg.min_bars}）: n={len(c)}")
    if not np.all(np.isfinite(c)) or not np.all(c > 0):
        raise ValueError("收盘价非法（须全部为正且有限）")
    if not np.all(np.isfinite(v)) or not np.all(v >= 0):
        raise ValueError("成交量非法（须全部 ≥0 且有限）")
    if ai_nlp_score is not None and not (0.0 <= float(ai_nlp_score) <= 100.0):
        raise ValueError(f"ai_nlp_score 非法（须 ∈ [0,100]）: {ai_nlp_score!r}")

    scorers = {
        "macd": _score_macd(c, cfg),
        "rsi": _score_rsi(c, cfg),
        "volume": _score_volume(c, v, cfg),
        "ma": _score_ma(c, cfg),
    }

    dimensions: list[DimensionScore] = []
    notes: list[str] = []
    for key in DIMENSION_KEYS:
        if key == "ai_nlp":
            if ai_nlp_score is None:
                dimensions.append(
                    DimensionScore(key=key, name_zh=_DIM_NAME_ZH[key], score=0.0, available=False, detail="未注入")
                )
                notes.append("AI NLP 维未注入（剔除该维，权重重归一）")
                continue
            dimensions.append(
                DimensionScore(
                    key=key,
                    name_zh=_DIM_NAME_ZH[key],
                    score=float(ai_nlp_score),
                    available=True,
                    detail="上游注入",
                )
            )
            continue
        score, detail = scorers[key]
        dimensions.append(
            DimensionScore(
                key=key,
                name_zh=_DIM_NAME_ZH[key],
                score=round(min(max(score, 0.0), 100.0), 4),
                available=True,
                detail=detail,
            )
        )

    num = sum(cfg.weight_of(d.key) * d.score for d in dimensions if d.available)
    den = sum(cfg.weight_of(d.key) for d in dimensions if d.available)
    strength = num / den if den > 0 else 50.0

    return StrengthResult(
        strength=round(min(max(strength, 0.0), 100.0), 2),
        label=_label_of(strength),
        dimensions=tuple(dimensions),
        ai_nlp_included=ai_nlp_score is not None,
        config=cfg,
        notes=tuple(notes),
    )
