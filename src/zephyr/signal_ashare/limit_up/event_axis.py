# [BLUEPRINT] MOD-SIG-146 | master_tc_night C232（波10 G-B.3 A股特有事件轴显式化）
# [MODULE] zephyr.signal_ashare.limit_up.event_axis
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（dataclasses/enum/datetime/typing）；连库零依赖（鸭子类型行注入，不 import 任何 zephyr 内部件）
# [CONSUMERS] （候选：涨停生态消费面——followthrough 双池口径的时间轴化表述；L02 情绪 c1/c2 簇事件化读数）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 事件互斥单选：SEALED 判定优先于 BUSTED，BUSTED 优先于 BROKEN（busted⊂broken 语义，单日单票至多一事件）；容差带 eps 仅吸收浮点表示误差（涨停价为 0.01 精度，eps 默认 1e-6 不作实质放宽）；无触板（high<limit-eps）=无事件（None，不造事件）；输入校验 fail-closed（OHLC 缺失/非有限/high<low/limit_price 非正即 ValueError）；PIT：事件仅由当日 OHLC×涨停价推导，不引用任何未来数据；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] master_tc_night/lanes/L6_factory/00_workbook.md C232 节
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（行字段缺失/非有限值/high<low/limit_price<=0/日期串非法，fail-closed）
# [TESTS] tests/signal_ashare/limit_up/test_event_axis.py
# [A_module] module_id=MOD-SIG-146 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""A股涨停生命周期事件轴显式层（MOD-SIG-146，波10 G-B.3）。

把散落在双池口径（limit_up_followthrough：sealed=昨封板 / broken=昨炸板）里的
涨停日终态，显式化为一等事件轴——每个（symbol, trade_date) 至多一个事件：

    SEALED  封板：close ≥ limit_price（收盘封住）
    BUSTED  开板炸：open ≥ limit_price 且 close < limit_price（开盘即板被砸开，
            全天未回封——broken 的真子集，最弱形态，单列防"炸板率"口径吞并）
    BROKEN  炸板：high ≥ limit_price 且 close < limit_price（盘中触板未封收）
    无事件：  high < limit_price（当日未曾触板）

判定顺序（互斥单选）：SEALED → BUSTED → BROKEN → None。
容差带 eps 只吸收浮点表示误差（A 股涨停价 0.01 精度），不做口径性放宽。

**结构事件轴（缠论）不在此重复实现**：分型/笔/段/中枢等结构事件由既有
`zephyr.signal_ashare.chanlun_structure`（MOD-SIG-072）承载，本模块与其正交
组合（事件轴=日终态离散事件；缠论轴=连续结构描摹），消费侧两轴各自取数。
`CHANLUN_AXIS_REF` 常量供接线处引用，禁造第二套缠论实现。

不做什么：不读库/不荐股/不触发交易——输出是事件描摹数据，非交易信号。

依据: 波10 G-B.3（dossier：A股特有事件轴显式化）；limit_up_followthrough
双池 sealed/broken 口径（MOD-SIG-141）；L02 c2 簇"炸板率未独立"缺口（G1）。
SSoT: depgraph node MOD-SIG-146（本 commit 随 apply_depgraph 登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 逐行 OHLC×limit_price 鸭子类型行序列
# 特征: 单行事件分类 / 轴级计数
# 算法: 互斥单选三段判定（SEALED→BUSTED→BROKEN）+ fail-closed 行校验
# 输出: EventAxisReport（events 元组 + 三类计数 + notes）
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "LimitUpEventType",
    "LimitUpEvent",
    "EventAxisReport",
    "CHANLUN_AXIS_REF",
    "classify_limit_up_event",
    "derive_event_axis",
]

# 缠论结构轴唯一承载件（禁在本包再造第二套分型/笔/中枢实现）
CHANLUN_AXIS_REF: Final = "zephyr.signal_ashare.chanlun_structure"


class LimitUpEventType(str, Enum):
    """涨停日终态事件（互斥单选，判定顺序 SEALED→BUSTED→BROKEN）。"""

    SEALED = "sealed"  # 封板：收盘封住
    BUSTED = "busted"  # 开板炸：开盘即板被砸开且收盘未回封（broken 真子集）
    BROKEN = "broken"  # 炸板：盘中触板、收盘未封


_DEFAULT_EPS: Final = 1e-6

_ROW_FIELDS: Final = ("symbol", "trade_date", "open", "high", "low", "close", "limit_price")


@dataclass(frozen=True, slots=True)
class LimitUpEvent:
    """单票单日涨停事件（JSON 可序列化）。"""

    symbol: str
    trade_date: str
    event_type: str  # LimitUpEventType.value
    open: float
    high: float
    low: float
    close: float
    limit_price: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EventAxisReport:
    """事件轴总产出（JSON 可序列化）。"""

    events: tuple[LimitUpEvent, ...]
    n_sealed: int
    n_busted: int
    n_broken: int
    n_rows: int  # 输入行数（含未触板行，供分母口径）
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_limit_up_event(
    open_: float,
    high: float,
    low: float,
    close: float,
    limit_price: float,
    eps: float = _DEFAULT_EPS,
) -> LimitUpEventType | None:
    """单行事件分类（互斥单选：SEALED→BUSTED→BROKEN→None）。

    Args:
        open_/high/low/close: 当日 OHLC。
        limit_price: 当日涨停价（stk_limit 轴，>0）。
        eps: 浮点容差（仅吸收表示误差，默认 1e-6）。

    Returns:
        LimitUpEventType 或 None（当日未触板=无事件）。

    Raises:
        ValueError: 任一价格非有限 / high<low / limit_price<=0。
    """
    prices = (open_, high, low, close, limit_price)
    if any(not math.isfinite(float(p)) for p in prices):
        raise ValueError(f"价格含非有限值: {prices!r}")
    o, h, lo, c, lp = (float(p) for p in prices)
    if lp <= 0:
        raise ValueError(f"limit_price 非法（须>0）: {lp}")
    if h < lo:
        raise ValueError(f"high<low 非法: high={h}, low={lo}")
    if h < lp - eps:
        return None  # 全天未触板
    if c >= lp - eps:
        return LimitUpEventType.SEALED
    if o >= lp - eps:
        return LimitUpEventType.BUSTED
    return LimitUpEventType.BROKEN


def _get_field(row: object, name: str) -> object:
    """鸭子类型取字段：dict 键优先，回落对象属性。"""
    if isinstance(row, dict):
        if name not in row:
            raise ValueError(f"行缺字段 {name!r}（fail-closed）")
        return row[name]
    if not hasattr(row, name):
        raise ValueError(f"行对象缺属性 {name!r}（fail-closed）")
    return getattr(row, name)


def _norm_date(value: object) -> str:
    """日期归一为 YYYY-MM-DD 串（str 原样过格式校验，date/datetime 取 isoformat）。"""
    if isinstance(value, str):
        date.fromisoformat(value)  # 非法即 ValueError
        return value
    if isinstance(value, (date, datetime)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    raise ValueError(f"trade_date 类型非法（str/date/datetime）: {value!r}")


def _bare(code: object) -> str:
    """symbol 归一为裸 6 位码口径（与 followthrough 双池一致；仅去空白）。"""
    s = str(code).strip()
    if not s:
        raise ValueError("symbol 不能为空（fail-closed）")
    return s


def derive_event_axis(rows: Sequence[Any], eps: float = _DEFAULT_EPS) -> EventAxisReport:
    """从既有涨停数据行推导事件轴（纯函数，零库依赖）。

    Args:
        rows: 逐行鸭子类型记录（dict 或带属性对象），字段=symbol/trade_date/
            open/high/low/close/limit_price（命名对齐 kline_daily×stk_limit 联算口径）。
        eps: 浮点容差透传 classify_limit_up_event。

    Returns:
        EventAxisReport：events（仅含触板行）+ 三类计数 + n_rows 分母。

    Raises:
        ValueError: 任一行校验失败（fail-closed，整轴拒绝）。
    """
    events: list[LimitUpEvent] = []
    n_sealed = n_busted = n_broken = 0
    for i, row in enumerate(rows):
        try:
            symbol = _bare(_get_field(row, "symbol"))
            trade_date = _norm_date(_get_field(row, "trade_date"))
            o = float(_get_field(row, "open"))
            h = float(_get_field(row, "high"))
            lo = float(_get_field(row, "low"))
            c = float(_get_field(row, "close"))
            lp = float(_get_field(row, "limit_price"))
        except ValueError:
            raise
        except (TypeError, AttributeError) as exc:
            raise ValueError(f"第 {i} 行字段不可解析（fail-closed）: {exc}") from exc
        et = classify_limit_up_event(o, h, lo, c, lp, eps=eps)
        if et is None:
            continue
        events.append(
            LimitUpEvent(
                symbol=symbol,
                trade_date=trade_date,
                event_type=et.value,
                open=o,
                high=h,
                low=lo,
                close=c,
                limit_price=lp,
            )
        )
        if et is LimitUpEventType.SEALED:
            n_sealed += 1
        elif et is LimitUpEventType.BUSTED:
            n_busted += 1
        else:
            n_broken += 1
    logger.info(
        "derive_event_axis: %d 行 → %d 事件（sealed=%d busted=%d broken=%d）",
        len(rows),
        len(events),
        n_sealed,
        n_busted,
        n_broken,
    )
    return EventAxisReport(
        events=tuple(events),
        n_sealed=n_sealed,
        n_busted=n_busted,
        n_broken=n_broken,
        n_rows=len(rows),
    )
