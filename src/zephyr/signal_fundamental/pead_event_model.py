# [BLUEPRINT] MOD-SIG-110 | docs/03_modules/_domain_fundamental_signal/pead_event_model/blueprint.md
# [MODULE] zephyr.signal_fundamental.pead_event_model
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] 无（判定核心纯内存；一致预期/EPS/价格序列全注入）
# [CONSUMERS] 运行时装配批（akshare 盈利预测免费源→一致预期注入 / c3 财务表实际 EPS 装配 / CTR-002 桥接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 判定核心纯内存无IO无触网; SUE 分母取 |一致预期| 且近零不可计算留痕; 分档阈值严格递增; 漂移收益窗口不足返回 None 不估算; 财报季窗口=日历日标记(交易日前移归 calendar_event_derivations); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_fundamental_signal/pead_event_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PeadEventError(占位 ZA-SIG-UNREGISTERED-PEAD)——空symbol/非有限EPS/空价格序列/非正窗口/起止倒置/阈值非递增时抛
# [TESTS] tests/signal_fundamental/test_pead_event_model.py
# [A_module] module_id=MOD-SIG-110 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
PeadEventModel — 财报季事件驱动与 PEAD 模型（MOD-SIG-110）。

B10-01417（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-FUNDAMEN-001，A1交易决策
架构 §4模块49）：PEAD（Post-Earnings-Announcement Drift，Bernard & Thomas
1989 经典异象）事件驱动件——**SUE 分档 + 20 日漂移收益统计 + 财报季持仓
标记**。

查重分工（蓝图 §0）：financial_parser=解析面 / announcement_provider=采集
面 / calendar_event_derivations=披露截止日历（本件财报季窗口为**日历日标
记**，交易日"遇假前移"口径归日历件，不重算）；SUE/漂移收益/持仓标记三
判定无既有件，独立缺口。

一致预期须用免费源（避免付费数据边界）：本件纯内存判定核心，EPS/一致预
期/价格序列全部 DI 注入，免费源绑定归运行时装配批。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: actual_eps 参数
#   fields: 参数 actual_eps，类型注解 float
#   code: pead_event_model.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: consensus_eps 参数
#   fields: 参数 consensus_eps，类型注解 float
#   code: pead_event_model.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: eps_floor 参数
#   fields: 参数 eps_floor（无注解）
#   code: pead_event_model.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: sue 参数
#   fields: 参数 sue，类型注解 float
#   code: pead_event_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_sue
#   name_en: compute_sue
#   intro: SUE = (实际EPS − 一致预期) / |一致预期|；近零预期 → None（不可计算）。
#   desc: SUE = (实际EPS − 一致预期) / |一致预期|；近零预期 → None（不可计算）。；源码 L233-L247
#   inputs: actual_eps consensus_eps eps_floor
#   outputs: float | None
# - id: A2
#   name_zh: ② classify_sue
#   name_en: classify_sue
#   intro: SUE 五档分档（sue < 阈值 严格小于归低档）。
#   desc: SUE 五档分档（sue < 阈值 严格小于归低档）。；源码 L250-L262
#   inputs: sue thresholds
#   outputs: SueBand
# - id: A3
#   name_zh: ③ compute_drift_return
#   name_en: compute_drift_return
#   intro: 事件日后 N 日漂移收益 close[t+N]/close[t] − 1；窗口不足 → None。
#   desc: 事件日后 N 日漂移收益 close[t+N]/close[t] − 1；窗口不足 → None。；源码 L265-L288
#   inputs: closes event_index days
#   outputs: float | None
# - id: A4
#   name_zh: ④ earnings_season_windows
#   name_en: earnings_season_windows
#   intro: 年度财报季窗口（4/30、8/31、10/31 前伸 pre_window 个日历日）。
#   desc: 年度财报季窗口（4/30、8/31、10/31 前伸 pre_window 个日历日）。；源码 L291-L304
#   inputs: year pre_window
#   outputs: tuple[EarningsSeasonWindow, ...]
# - id: A5
#   name_zh: ⑤ PeadEventModel
#   name_en: PeadEventModel
#   intro: PEAD 事件驱动判定核心（配置持有 + 事件评估 + 财报季标记）。
#   desc: PEAD 事件驱动判定核心（配置持有 + 事件评估 + 财报季标记）。；公共方法（定义序）: evaluate, earnings_season_mark；源码 L307-L386
#   inputs: thresholds drift_days eps_floor pre_window
#   outputs: 返回值
#   （注：A5 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float | None
#   name_en: float | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（akshare 盈利预测免费源→一致预期注入 / c3 财务表实际 EPS 装配 / CTR-002 桥接）
# - id: O2
#   name_zh: SueBand
#   name_en: SueBand
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（akshare 盈利预测免费源→一致预期注入 / c3 财务表实际 EPS 装配 / CTR-002 桥接）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "EarningsEvent",
    "EarningsSeasonMark",
    "EarningsSeasonWindow",
    "PeadEventError",
    "PeadEventModel",
    "PeadResult",
    "SueBand",
    "SueThresholds",
    "classify_sue",
    "compute_drift_return",
    "compute_sue",
    "earnings_season_windows",
]

_EPS_FLOOR: Final[float] = 1e-6  # 一致预期近零防爆炸
_DEFAULT_DRIFT_DAYS: Final[int] = 20  # PEAD 经典 20 日漂移窗口
_PRE_WINDOW_DAYS: Final[int] = 10  # 财报季窗口前伸日历日

#: 财报强制披露截止（月/日），语义对齐 calendar_event_derivations
#: derive_earnings_deadline（4/30 年报+一季报、8/31 半年报、10/31 三季报）；
#: 本件只取日历日，"遇非交易日前移"由日历件在装配侧完成。
_EARNINGS_DEADLINES: Final[tuple[tuple[int, int], ...]] = ((4, 30), (8, 31), (10, 31))


class PeadEventError(Exception):
    """PEAD 事件判定输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-PEAD。
    """


class SueBand(str, Enum):
    """SUE 五档分档。"""

    STRONG_NEGATIVE = "strong_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    STRONG_POSITIVE = "strong_positive"


@dataclass(frozen=True)
class SueThresholds:
    """SUE 分档阈值（严格递增；sue < 阈值 归低档）。"""

    strong_neg: float = -2.0
    neg: float = -0.5
    neutral: float = 0.5
    pos: float = 2.0

    def __post_init__(self) -> None:
        vals = (self.strong_neg, self.neg, self.neutral, self.pos)
        if any(not math.isfinite(v) for v in vals):
            raise PeadEventError("SUE 分档阈值须为有限值")
        if not (self.strong_neg < self.neg < self.neutral < self.pos):
            raise PeadEventError(f"SUE 分档阈值须严格递增: {vals}")


@dataclass(frozen=True)
class EarningsEvent:
    """财报披露事件（EPS/一致预期注入）。"""

    symbol: str
    announce_date: datetime.date
    actual_eps: float
    consensus_eps: float


@dataclass(frozen=True)
class PeadResult:
    """PEAD 事件判定结果。"""

    symbol: str
    announce_date: datetime.date
    sue: float | None
    band: SueBand | None
    drift_return: float | None
    drift_days: int
    computable: bool
    detail: str = ""


@dataclass(frozen=True)
class EarningsSeasonWindow:
    """财报季窗口（日历日标记）。"""

    deadline: datetime.date
    window_start: datetime.date
    window_end: datetime.date


@dataclass(frozen=True)
class EarningsSeasonMark:
    """财报季持仓标记。"""

    symbol: str
    in_season: bool
    exposure: bool
    window_start: datetime.date | None = None
    window_end: datetime.date | None = None


def _require_finite(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise PeadEventError(f"{name} 须为有限值: {value!r}")
    return value


def compute_sue(
    actual_eps: float,
    consensus_eps: float,
    *,
    eps_floor: float = _EPS_FLOOR,
) -> float | None:
    """SUE = (实际EPS − 一致预期) / |一致预期|；近零预期 → None（不可计算）。"""
    _require_finite("actual_eps", actual_eps)
    _require_finite("consensus_eps", consensus_eps)
    if eps_floor <= 0:
        raise PeadEventError("eps_floor 须为正")
    denom = abs(consensus_eps)
    if denom < eps_floor:
        return None
    return (actual_eps - consensus_eps) / denom


def classify_sue(sue: float, *, thresholds: SueThresholds | None = None) -> SueBand:
    """SUE 五档分档（sue < 阈值 严格小于归低档）。"""
    _require_finite("sue", sue)
    th = thresholds or SueThresholds()
    if sue < th.strong_neg:
        return SueBand.STRONG_NEGATIVE
    if sue < th.neg:
        return SueBand.NEGATIVE
    if sue < th.neutral:
        return SueBand.NEUTRAL
    if sue < th.pos:
        return SueBand.POSITIVE
    return SueBand.STRONG_POSITIVE


def compute_drift_return(
    closes: Sequence[float],
    event_index: int,
    *,
    days: int = _DEFAULT_DRIFT_DAYS,
) -> float | None:
    """事件日后 N 日漂移收益 close[t+N]/close[t] − 1；窗口不足 → None。"""
    if days <= 0:
        raise PeadEventError("漂移窗口 days 须为正")
    if event_index < 0:
        raise PeadEventError("event_index 须非负")
    if not closes:
        raise PeadEventError("价格序列为空")
    for i, c in enumerate(closes):
        _require_finite(f"closes[{i}]", c)
    base = closes[event_index] if event_index < len(closes) else None
    if base is None:
        raise PeadEventError(f"event_index 越界: {event_index} >= {len(closes)}")
    if base == 0.0:
        raise PeadEventError("基准收盘价为 0，不可计算漂移收益")
    end = event_index + days
    if end >= len(closes):
        return None
    return closes[end] / base - 1.0


def earnings_season_windows(
    year: int,
    *,
    pre_window: int = _PRE_WINDOW_DAYS,
) -> tuple[EarningsSeasonWindow, ...]:
    """年度财报季窗口（4/30、8/31、10/31 前伸 pre_window 个日历日）。"""
    if pre_window <= 0:
        raise PeadEventError("pre_window 须为正")
    out: list[EarningsSeasonWindow] = []
    for month, day in _EARNINGS_DEADLINES:
        deadline = datetime.date(year, month, day)
        start = deadline - datetime.timedelta(days=pre_window)
        out.append(EarningsSeasonWindow(deadline=deadline, window_start=start, window_end=deadline))
    return tuple(out)


class PeadEventModel:
    """PEAD 事件驱动判定核心（配置持有 + 事件评估 + 财报季标记）。"""

    def __init__(
        self,
        *,
        thresholds: SueThresholds | None = None,
        drift_days: int = _DEFAULT_DRIFT_DAYS,
        eps_floor: float = _EPS_FLOOR,
        pre_window: int = _PRE_WINDOW_DAYS,
    ) -> None:
        if drift_days <= 0:
            raise PeadEventError("drift_days 须为正")
        if eps_floor <= 0:
            raise PeadEventError("eps_floor 须为正")
        if pre_window <= 0:
            raise PeadEventError("pre_window 须为正")
        self._thresholds = thresholds or SueThresholds()
        self._drift_days = drift_days
        self._eps_floor = eps_floor
        self._pre_window = pre_window

    def evaluate(
        self,
        event: EarningsEvent,
        closes: Sequence[float],
        event_index: int,
    ) -> PeadResult:
        """单事件评估：SUE + 分档 + 漂移收益（近零预期不可计算留痕）。"""
        if not event.symbol:
            raise PeadEventError("symbol 为空")
        sue = compute_sue(event.actual_eps, event.consensus_eps, eps_floor=self._eps_floor)
        drift = compute_drift_return(closes, event_index, days=self._drift_days)
        if sue is None:
            detail = f"consensus_eps 近零(|{event.consensus_eps}| < {self._eps_floor})，SUE 不可计算（留痕不静默丢弃）"
            _log.warning("PEAD 不可计算: %s %s", event.symbol, detail)
            return PeadResult(
                symbol=event.symbol,
                announce_date=event.announce_date,
                sue=None,
                band=None,
                drift_return=drift,
                drift_days=self._drift_days,
                computable=False,
                detail=detail,
            )
        return PeadResult(
            symbol=event.symbol,
            announce_date=event.announce_date,
            sue=sue,
            band=classify_sue(sue, thresholds=self._thresholds),
            drift_return=drift,
            drift_days=self._drift_days,
            computable=True,
            detail="",
        )

    def earnings_season_mark(
        self,
        symbol: str,
        hold_start: datetime.date,
        hold_end: datetime.date,
        *,
        year: int,
    ) -> EarningsSeasonMark:
        """财报季持仓标记：持仓区间与任一财报季窗口相交 → exposure。"""
        if not symbol:
            raise PeadEventError("symbol 为空")
        if hold_end < hold_start:
            raise PeadEventError(f"持仓区间起止倒置: {hold_start} > {hold_end}")
        for w in earnings_season_windows(year, pre_window=self._pre_window):
            if hold_start <= w.window_end and hold_end >= w.window_start:
                return EarningsSeasonMark(
                    symbol=symbol,
                    in_season=True,
                    exposure=True,
                    window_start=w.window_start,
                    window_end=w.window_end,
                )
        return EarningsSeasonMark(symbol=symbol, in_season=False, exposure=False)
