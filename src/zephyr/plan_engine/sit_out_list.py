# [BLUEPRINT] MOD-PLAN-014 | 待统筹登记（缺口总账 GAP-F-05 + 45号作战手册 §4 W5）
# [MODULE] zephyr.plan_engine.sit_out_list
# [DOMAIN] D_PLAN
# [DEPENDENCIES] none（三源全部注入：事件日历实例/止损状态/作战池清单——数据源接线属上游装配）
# [CONSUMERS] 作战室 W5 禁做清单警示条（违反=预案外操作，W0 归因记执行不一致）; （候选：盘前管线预案过滤）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三源合成（event_calendar 实例+止损状态+作战池规则）；blackout 级事件才进清单（caution 仅计数留痕）；止损禁反手恒当日（T 日止损 T 日禁反手）；池外不碰=毯式规则（war_pool 注入即激活，空池=全禁）；本模块纯函数零 DB/CH（三源数据全部注入）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-05 行
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（日期格式/scope/severity/end_date 次序非法 fail-closed）
# [TESTS] tests/plan_engine/test_sit_out_list.py
# [A_module] module_id=MOD-PLAN-014 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""SitOutList — 禁做清单生成器 (MOD-PLAN-014)

缺口总账 GAP-F-05（=前端设计文档缺口⑩）落码：作战室 W5 禁做清单警示条
（机构风险包络四件套④，45号 §3.3）。三源→sit-out list 合成逻辑：

    ① 事件时段禁交易（event_calendar 实例：议息/交割/披露窗口 blackout 级，
       支持 event_date~end_date 窗口；caution 级不进清单仅计数留痕）；
    ② 止损后禁反手（当日止损标的当日 NO_REVERSE——A 股 T+1 下反手=情绪化
       追回高发区，45号 W5 口径）；
    ③ 跌停不撬板（limit_down 标的 NO_BUY）；
    ④ 池外不碰（作战池 GAP-F-06 产出注入即激活毯式规则：池外标的默认
       禁新开仓；空池=全禁"池外不碰日"；war_pool=None=规则不激活）。

违反禁做清单=预案外操作，W0 三维归因记"执行不一致"（45号 §4 W5 联动契约）。

不做什么：事件实例采集/止损状态机/作战池计算均不在本模块（三源注入，
         上游装配职责）/不下单/不做盘中实时刷新（盘前批处理产出）。

依据: 缺口总账 GAP-F-05；45_warroom_playbook §3.3④/§4 W5
SSoT: depgraph MOD-PLAN-014（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + events(事件日历实例) + stopped_symbols(当日止损) + limit_down_symbols(跌停) + war_pool_symbols(作战池)
# 特征: blackout 窗口覆盖判定 / 当日止损判定 / 池外判定
# 算法: 三源规则合成 → SitOutEntry 清单 + 毯式池规则
# 输出: SitOutList（entries/pool_rule_active/is_sit_out 查询，纯 frozen dataclass JSON 可序列化）
"""

from __future__ import annotations

import datetime
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Final

__all__: Final = [
    "RULE_EVENT_BLACKOUT",
    "RULE_LIMIT_DOWN_NO_DIP",
    "RULE_OUT_OF_POOL",
    "RULE_STOP_LOSS_NO_REVERSE",
    "CalendarEvent",
    "SitOutEntry",
    "SitOutList",
    "StoppedSymbol",
    "build_sit_out_list",
]

# ── 规则枚举（冻结词表，W5 四条）──

RULE_EVENT_BLACKOUT: Final = "EVENT_BLACKOUT"  # 事件时段禁交易
RULE_STOP_LOSS_NO_REVERSE: Final = "STOP_LOSS_NO_REVERSE"  # 止损后禁反手
RULE_LIMIT_DOWN_NO_DIP: Final = "LIMIT_DOWN_NO_DIP"  # 跌停不撬板
RULE_OUT_OF_POOL: Final = "OUT_OF_POOL"  # 池外不碰

_SCOPES: Final = frozenset({"market", "sector", "symbol"})
_SEVERITIES: Final = frozenset({"info", "caution", "blackout"})
_DATE_RE: Final = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_date(v: object, name: str) -> str:
    """YYYY-MM-DD 严格校验（fail-closed）。"""
    if not isinstance(v, str) or not _DATE_RE.fullmatch(v):
        raise ValueError(f"{name} 非法（须 YYYY-MM-DD）: {v!r}")
    try:
        datetime.date.fromisoformat(v)
    except ValueError as exc:
        raise ValueError(f"{name} 非真实日期: {v!r}") from exc
    return v


# ── 输入契约 ──


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    """事件日历实例（event_calendar 注册表类型的事件实例，上游装配注入）。

    Attributes:
        event_date: 事件起始日 YYYY-MM-DD
        event_type: 事件类型（EVT-* 语义，自由字符串留痕）
        scope: 作用域 market/sector/symbol
        target: 作用目标（sector_code/symbol；market 级 None）
        severity: info/caution/blackout（仅 blackout 进禁做清单）
        name: 事件名（中文可审计）
        end_date: 窗口结束日（None=单日事件）
        source: 数据源标识（留痕可回查）
    """

    event_date: str
    event_type: str
    scope: str
    target: str | None
    severity: str
    name: str
    end_date: str | None = None
    source: str = "event_calendar"

    def __post_init__(self) -> None:
        _validate_date(self.event_date, "event_date")
        if self.end_date is not None:
            _validate_date(self.end_date, "end_date")
            if self.end_date < self.event_date:
                raise ValueError(f"end_date 早于 event_date: {self.end_date!r} < {self.event_date!r}")
        if self.scope not in _SCOPES:
            raise ValueError(f"scope 非法（合法={sorted(_SCOPES)}）: {self.scope!r}")
        if self.severity not in _SEVERITIES:
            raise ValueError(f"severity 非法（合法={sorted(_SEVERITIES)}）: {self.severity!r}")
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError(f"event_type 非法（须非空字符串）: {self.event_type!r}")
        if self.scope == "symbol" and not (self.target and str(self.target).strip()):
            raise ValueError("scope=symbol 时 target 必须非空")

    def covers(self, trade_date: str) -> bool:
        """事件窗口是否覆盖交易日。"""
        return self.event_date <= trade_date <= (self.end_date or self.event_date)


@dataclass(frozen=True, slots=True)
class StoppedSymbol:
    """当日止损标的（止损状态源注入，止损后禁反手规则输入）。"""

    symbol: str
    stopped_at: str  # 止损触发日 YYYY-MM-DD
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(f"symbol 非法（须非空字符串）: {self.symbol!r}")
        _validate_date(self.stopped_at, "stopped_at")


# ── 输出契约 ──


@dataclass(frozen=True, slots=True)
class SitOutEntry:
    """禁做清单条目（一规则一目标一行）。"""

    rule: str  # RULE_* 四规则之一
    scope: str  # market/sector/symbol/portfolio（portfolio=毯式池规则）
    target: str | None  # 作用目标（sector_code/symbol；market/portfolio 级 None）
    action: str  # NO_TRADE / NO_BUY / NO_REVERSE
    reason: str  # 中文理由（可审计）
    source: str  # 来源（event_calendar/stop_loss/limit_down/war_pool）


@dataclass(frozen=True, slots=True)
class SitOutList:
    """禁做清单输出契约（盘前批处理产出，W5 警示条消费）。"""

    trade_date: str
    entries: list[SitOutEntry] = field(default_factory=list)
    pool_symbols: list[str] | None = None  # 作战池清单（None=池规则不激活）
    pool_rule_active: bool = False  # 池外不碰毯式规则是否激活
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def is_sit_out(self, symbol: str, *, action: str = "NO_TRADE") -> bool:
        """标的是否命中禁做（symbol/market 级精确 + 池外毯式；sector 级由调用方映射）。

        Args:
            symbol: 标的代码。
            action: 禁做动作过滤（默认 NO_TRADE 只查全禁；NO_BUY/NO_REVERSE 查对应动作；
                市场级 NO_TRADE 事件对任何 action 查询均命中——全禁优先）。
        """
        for e in self.entries:
            if e.rule == RULE_OUT_OF_POOL:
                continue  # 毯式规则单独判定
            if e.action != action and e.action != "NO_TRADE":
                continue
            if e.scope == "market":
                return True
            if e.scope == "symbol" and e.target == symbol:
                return True
        if self.pool_rule_active and action == "NO_TRADE":
            return symbol not in set(self.pool_symbols or [])
        return False

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)


# ── 合成主入口（纯函数）──


def build_sit_out_list(
    trade_date: str,
    *,
    events: list[CalendarEvent] | tuple[CalendarEvent, ...] = (),
    stopped_symbols: list[StoppedSymbol] | tuple[StoppedSymbol, ...] = (),
    limit_down_symbols: list[str] | tuple[str, ...] = (),
    war_pool_symbols: list[str] | tuple[str, ...] | None = None,
) -> SitOutList:
    """三源合成禁做清单（45号 W5 四规则）。

    Args:
        trade_date: 交易日 YYYY-MM-DD（fail-closed）。
        events: 事件日历实例清单（blackout 级且窗口覆盖当日 → NO_TRADE）。
        stopped_symbols: 止损状态清单（当日止损 → NO_REVERSE）。
        limit_down_symbols: 跌停标的清单（→ NO_BUY 不撬板）。
        war_pool_symbols: 作战池清单（None=池规则不激活；注入含空清单=激活，
            空池=全禁"池外不碰日"）。

    Returns:
        SitOutList（entries 按规则序合成，JSON 可序列化）。

    Raises:
        ValueError: trade_date 非法（fail-closed）。
    """
    v_date = _validate_date(trade_date, "trade_date")
    entries: list[SitOutEntry] = []
    notes: list[str] = []
    annotations: list[str] = []

    # ① 事件时段禁交易（blackout 才进清单；caution 计数留痕）
    n_caution = 0
    for ev in events:
        if not ev.covers(v_date):
            continue
        if ev.severity == "blackout":
            entries.append(
                SitOutEntry(
                    rule=RULE_EVENT_BLACKOUT,
                    scope=ev.scope,
                    target=ev.target,
                    action="NO_TRADE",
                    reason=f"事件禁交易：{ev.name}（{ev.event_type}，窗口 {ev.event_date}~{ev.end_date or ev.event_date}）",
                    source=ev.source,
                )
            )
        elif ev.severity == "caution":
            n_caution += 1
    if n_caution:
        notes.append(f"caution 级事件 {n_caution} 条当日生效（提示级不进禁做清单）")

    # ② 止损后禁反手（当日）
    for s in stopped_symbols:
        if s.stopped_at == v_date:
            entries.append(
                SitOutEntry(
                    rule=RULE_STOP_LOSS_NO_REVERSE,
                    scope="symbol",
                    target=s.symbol,
                    action="NO_REVERSE",
                    reason=f"当日止损禁反手：{s.symbol}（{s.reason or '止损触发'}，T 日止损 T 日不追回）",
                    source="stop_loss",
                )
            )

    # ③ 跌停不撬板
    for sym in limit_down_symbols:
        entries.append(
            SitOutEntry(
                rule=RULE_LIMIT_DOWN_NO_DIP,
                scope="symbol",
                target=str(sym),
                action="NO_BUY",
                reason=f"跌停不撬板：{sym}（跌停封死不接飞刀）",
                source="limit_down",
            )
        )

    # ④ 池外不碰（毯式规则）
    pool_active = war_pool_symbols is not None
    pool_list = [str(s) for s in war_pool_symbols] if war_pool_symbols is not None else None
    if pool_active:
        n = len(pool_list or [])
        entries.append(
            SitOutEntry(
                rule=RULE_OUT_OF_POOL,
                scope="portfolio",
                target=None,
                action="NO_TRADE",
                reason=f"池外不碰：作战池 {n} 票之外不新开仓（注意力也是风险预算）" if n else "池外不碰日：作战池空，全面禁新开仓",
                source="war_pool",
            )
        )

    if not entries:
        annotations.append("今日禁做清单空（无 blackout 事件/无当日止损/无跌停/池规则未激活）")
    else:
        annotations.append(f"今日禁做清单 {len(entries)} 条（违反=预案外操作，W0 归因记执行不一致）")

    return SitOutList(
        trade_date=v_date,
        entries=entries,
        pool_symbols=pool_list,
        pool_rule_active=pool_active,
        annotations=annotations,
        notes=notes,
    )
