# [BLUEPRINT] MOD-INT-EVENT-FACTOR | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.4
# [MODULE] zephyr.intelligence.event_factor_matrix
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pandas
# [CONSUMERS] 事件驱动 sleeve（六因子矩阵数值项，event_impact_score = w1·ORJ_z + w2·dReport_z + w3·Jump_on_PEAD_z + w4·overnight_trend_z 的因子输入；权重待 G10 校准）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] dReport 正值=提前披露；Jump on PEAD 阈值默认 3%（与 PEAD Inversion 极端反应口径一致，G23 待校准）；隔夜趋势首值 NaN（无前收）+ rolling 满窗才出值；AStockEvent Feed 远期不做（26 号 §2.4 登记）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.4
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventFactorError(ZA-INT-0004)——输入契约违反（序列长度不一致/窗口非法）时抛
# [TESTS] tests/intelligence/test_event_factor_matrix.py
# [A_module] module_id=MOD-INT-EVENT-FACTOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.4 事件驱动六因子矩阵（v1.5.0）
# [ALGO_FLOW]
# I1: 法定披露截止日+实际披露日 / 公告后 5 日每日异常收益 / OHLC 开收序列
# F1: compute_dreport = 截止日 - 实际披露日（正值=提前）
# F2: compute_jump_on_pead = 5 日窗口内 |AR|≥阈值的跳跃分量（保号求和），drift=余项
# F3: compute_overnight_trend = (open_t/close_{t-1}-1) 的 20 日滚动均值
# O1: int / JumpDecomposition / pd.Series（原始因子值，z-score 归一化归因子工厂）
# [/ALGO_FLOW]
"""MOD-INT-EVENT-FACTOR — 事件驱动六因子矩阵数值项（26 号 §2.4 v1.5.0 施工化）。

三项待施工数值因子（实证齐备、优先级最高，NLP 管道未就绪前的数值 alpha 补充，
与 ORJ 同属降级算法、不依赖 NLP）：

- **dReport**（披露日提前天数）：``dReport = 法定披露截止日 - 实际披露日``
  （正值=提前）。招商证券 10 年回测年化超额 4.88%/Sharpe 1.44；大幅提前 T+5
  上涨概率 70-75%。
- **Jump on PEAD**（公告后价格跳跃）：公告后 5 日窗口 CAR 的跳跃分量——
  |日异常收益| ≥ 阈值（默认 3%，与 §2.4 PEAD Inversion 极端反应口径一致）
  的保号分量求和；余项为 drift。华泰金工 5 日 IC=10.96%。
- **隔夜趋势**：隔夜收益率（``open_t/close_{t-1} - 1``）20 日滚动均值。
  西部证券 Rank IC=-0.1687（负向）、中证 2000 年化超额 7.97%——本模块只产出
  原始趋势值，方向使用归下游。

ORJ / PEAD Inversion 两因子已在 event_score.py 承载（overnight_return_jump /
extreme_reaction_modifier 口径），本模块不重复。AStockEvent Feed 远期不做
（26 号 §2.4 登记）。z-score 归一化与权重融合（event_impact_score）待 G10 校准，
归因子工厂/选股漏斗，不在本模块。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.4
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Final, Sequence

import pandas as pd

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]


class EventFactorError(ZephyrBaseError):
    """ZA-INT-0004: 六因子数值项输入契约违反。"""

    error_code = "ZA-INT-0004"


# ── 参数常量（G23/G10 待校准，26 号 §2.4 登记）──
JUMP_ON_PEAD_WINDOW: Final[int] = 5  # 公告后窗口（交易日）
JUMP_ON_PEAD_THRESHOLD: Final[float] = 0.03  # 跳跃判定阈值（对齐 PEAD Inversion 3%）
OVERNIGHT_TREND_WINDOW: Final[int] = 20  # 隔夜趋势滚动窗口（西部证券口径）


def compute_dreport(statutory_deadline: date, actual_disclosure_date: date) -> int:
    """dReport = 法定披露截止日 - 实际披露日（自然日，正值=提前）。

    招商证券 10 年回测：年化超额 4.88%/Sharpe 1.44；大幅提前 T+5 上涨概率 70-75%。
    负值 = 延后披露（财报难产嫌疑，利空维度）。
    """
    return (statutory_deadline - actual_disclosure_date).days


@dataclass(frozen=True, slots=True)
class JumpDecomposition:
    """Jump on PEAD 分解结果。

    jump_component : 5 日窗口内 |AR|≥阈值的跳跃分量（保号求和）——因子值。
    drift_component : 余项（温和日分量）。
    car_total : 窗口 CAR 合计 = jump + drift。
    """

    jump_component: float
    drift_component: float
    car_total: float


def compute_jump_on_pead(
    daily_abnormal_returns: Sequence[float],
    jump_threshold: float = JUMP_ON_PEAD_THRESHOLD,
) -> JumpDecomposition:
    """Jump on PEAD：公告后 5 日窗口 CAR 的跳跃分量（华泰金工 5 日 IC=10.96%）。

    Parameters
    ----------
    daily_abnormal_returns : 公告后窗口每日异常收益序列（建议 5 日，
        ``JUMP_ON_PEAD_WINDOW``；长度不限定，逐日判定）。
    jump_threshold : 跳跃判定阈值 |AR|（默认 3%，G23 待校准）。

    Returns
    -------
    JumpDecomposition —— jump_component 保号求和（正跳+负跳抵消），
    drift_component 为 |AR|<阈值日的合计，car_total = jump + drift。
    空输入 → 全零。
    """
    if jump_threshold <= 0:
        raise EventFactorError(f"compute_jump_on_pead: jump_threshold 须 >0，实际 {jump_threshold}")
    jump = 0.0
    drift = 0.0
    for ar in daily_abnormal_returns:
        ar_f = float(ar)
        if abs(ar_f) >= jump_threshold:
            jump += ar_f
        else:
            drift += ar_f
    return JumpDecomposition(
        jump_component=jump,
        drift_component=drift,
        car_total=jump + drift,
    )


def compute_overnight_trend(
    opens: pd.Series,
    closes: pd.Series,
    window: int = OVERNIGHT_TREND_WINDOW,
) -> pd.Series:
    """隔夜趋势：隔夜收益率 20 日滚动均值（西部证券 Rank IC=-0.1687）。

    隔夜收益率 = ``open_t / close_{t-1} - 1``（A 股 T+1 天然隔夜窗口，
    与事件日 ORJ 时序扩展同源——26 号 §2.4 协同：事件日 ORJ>3% +
    20 日隔夜趋势为正 = 强信号叠加）。

    Parameters
    ----------
    opens / closes : 开盘价/收盘价序列（等长、同索引、时间升序）。
    window : 滚动窗口（默认 20 交易日）。

    Returns
    -------
    pd.Series —— 与输入同索引；首值 NaN（无前收），前 window 个有效隔夜
    收益未满窗亦为 NaN。close_{t-1} ≤ 0 的位置产出 inf/NaN 原样保留
    （数据质量归上游 DQ 治理）。
    """
    if len(opens) != len(closes):
        raise EventFactorError(f"compute_overnight_trend: 两序列长度不一致 opens={len(opens)} closes={len(closes)}")
    if window < 1:
        raise EventFactorError(f"compute_overnight_trend: window 须 ≥1，实际 {window}")
    overnight_returns = opens / closes.shift(1) - 1.0
    return overnight_returns.rolling(window, min_periods=window).mean()


__all__: Final = [
    "JUMP_ON_PEAD_WINDOW",
    "JUMP_ON_PEAD_THRESHOLD",
    "OVERNIGHT_TREND_WINDOW",
    "EventFactorError",
    "JumpDecomposition",
    "compute_dreport",
    "compute_jump_on_pead",
    "compute_overnight_trend",
]
