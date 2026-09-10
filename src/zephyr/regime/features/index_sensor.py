# [BLUEPRINT] MOD-REGIME-016 | docs/03_modules/_domain_regime/index_sensor/blueprint.md
# [MODULE] zephyr.regime.features.index_sensor
# [DOMAIN] D_REGIME
# [DEPENDENCIES] 无（纯函数核，零 IO；指数日线由调用方从 DS-150 算好注入）
# [CONSUMERS] TDM-E-L1-S1（大盘指数传感器）；TDM-E-L1-AGG（L1 聚合输入）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 输出趋势分恒 ∈[-2,+2](clamp); MA20>MA60 多头+1; 收盘破 MA20 减一档、破 MA60 减两档(叠加式); 距 60 日高点<3% 高位减 1; 序列升序时间且最新在末位(只用≤t 数据无前视); 样本<61 根 fail-closed 抛错; 同输入必同输出(frozen); 均线用简单移动平均(标准口径)
# [MODIFY-GUARD] docs/03_modules/_domain_regime/index_sensor/blueprint.md + 地图节点 TDM-E-L1-S1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 样本不足/非法序列（NaN/负价/降序）→ IndexSensorError（fail-closed）
# [TESTS] tests/regime/test_index_sensor.py
# [TTL] permanent
"""IndexSensor — 大盘指数传感器：均线排列+位置打分（MOD-REGIME-016）。

节点语义逐条吸收（真源=TDM-E-L1-S1 algo_note）：
- 看 MA20/MA60 排列与位置：MA20 在 MA60 上=多头加分；
  指数距 60 日高点<3%=高位减分；破 MA20 减一档、破 MA60 减两档。
- 输出指数趋势分（-2~+2）：+2 强势 / +1 偏多 / 0 中性 / -1 偏弱 / -2 弱势。

打分模型（叠加后 clamp 到 [-2,+2]，同输入必同输出）：
  start=0
  +1  MA20 > MA60（多头排列；反之不加分——节点只定义多头加分）
  -1  收盘 < MA20（破位减一档）
  -2  收盘 < MA60（破年线级减两档；与破 MA20 叠加）
  -1  距 60 日滚动高点 < 3%（高位减分——高位不远攻）
  clamp [-2, +2]

查重分工（蓝图 §1）：index_regime_panel（MOD-REGIME-008）=HMM 七态概率面板
（概率分布视角）；本件=均线排列+位置的**规则打分**（-2~+2 单一分值视角），
节点 algo_note 明文口径是后者；两者同为 L1-S1 的输入件，互不替代。
D109 攻防板块特征（券商/银行 5 日超额）归 sector 层特征件，不在本件。
"""

from __future__ import annotations

from dataclasses import dataclass

_WINDOW_MA_FAST = 20
_WINDOW_MA_SLOW = 60
_HIGH_LOOKBACK = 60
_HIGH_PROXIMITY = 0.03  # 距 60 日高点 <3% = 高位
_SCORE_MIN = -2
_SCORE_MAX = 2


class IndexSensorError(ValueError):
    """非法输入（fail-closed）：样本不足/NaN/负价/序列过短。"""


@dataclass(frozen=True)
class IndexTrendScore:
    """指数趋势打分（frozen，可审计）。"""

    score: int  # ∈ [-2, +2]
    ma20: float
    ma60: float
    high60: float
    dist_to_high: float  # (high60-close)/high60 ∈ [0,1)
    above_ma20: bool
    above_ma60: bool
    bullish_alignment: bool  # MA20 > MA60
    near_60d_high: bool  # 距高点 <3%
    reasons: tuple[str, ...]


def _validate_closes(closes: tuple[float, ...]) -> None:
    if len(closes) < _WINDOW_MA_SLOW + 1:
        raise IndexSensorError(
            f"样本不足：至少需 {_WINDOW_MA_SLOW + 1} 根收盘价（MA60+当日），got {len(closes)}"
        )
    for i, c in enumerate(closes):
        if c != c or c <= 0:  # NaN 或非正
            raise IndexSensorError(f"非法收盘价（NaN/负数）index={i}: {c}")


def _sma(values: tuple[float, ...], window: int, end: int) -> float:
    """简单移动平均：values[end-window+1 .. end] 的均值。"""
    return sum(values[end - window + 1 : end + 1]) / window


def compute_index_trend_score(closes: tuple[float, ...]) -> IndexTrendScore:
    """指数趋势打分（纯函数；closes 升序时间、末位=最新；只用 ≤t 数据）。

    Args:
        closes: 指数日线收盘价序列（≥61 根：MA60 窗口 + 当日）。

    Returns:
        IndexTrendScore：score ∈ [-2, +2]。
    """
    if not isinstance(closes, tuple):
        closes = tuple(closes)
    _validate_closes(closes)

    latest = closes[-1]
    ma20 = _sma(closes, _WINDOW_MA_FAST, len(closes) - 1)
    ma60 = _sma(closes, _WINDOW_MA_SLOW, len(closes) - 1)
    high60 = max(closes[-_HIGH_LOOKBACK:])
    dist_to_high = (high60 - latest) / high60

    above_ma20 = latest > ma20
    above_ma60 = latest > ma60
    bullish_alignment = ma20 > ma60
    near_60d_high = dist_to_high < _HIGH_PROXIMITY

    score = 0
    reasons: list[str] = []
    if bullish_alignment:
        score += 1
        reasons.append("MA20>MA60 多头排列 +1")
    if not above_ma20:
        score -= 1
        reasons.append("收盘破 MA20 -1")
    if not above_ma60:
        score -= 2
        reasons.append("收盘破 MA60 -2")
    if near_60d_high:
        score -= 1
        reasons.append("距 60 日高点<3% 高位减分 -1")

    score = max(_SCORE_MIN, min(_SCORE_MAX, score))
    return IndexTrendScore(
        score=score,
        ma20=ma20,
        ma60=ma60,
        high60=high60,
        dist_to_high=dist_to_high,
        above_ma20=above_ma20,
        above_ma60=above_ma60,
        bullish_alignment=bullish_alignment,
        near_60d_high=near_60d_high,
        reasons=tuple(reasons),
    )
