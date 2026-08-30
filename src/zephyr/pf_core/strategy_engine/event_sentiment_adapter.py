# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine.event_sentiment_adapter
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] pandas; zephyr.intelligence.event_score; zephyr.pf_core.strategies.event_driven_sleeve_strategy; zephyr.data.ch_reader（lazy）
# [CONSUMERS] 事件策略回测跑批（.runtime 施工件）；zephyr.pf_core.strategy_engine（lazy re-export）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] PIT：交易日 T 消费窗口 [T-1 18:00, T 08:00) 情绪分（window_date=T-1 自然日，收盘于开盘前）；防未来函数护栏——window_date>T-1 的记录硬剔除不消费（window_date 缺省 None=源未携带，放行兼容）；面板 symbol 与 load_history 同源（纯数字代码，canonical 去后缀）；权重和<=1.0（策略侧不变量透传）；情绪分作事件方向触发维度非截面排序（26号 §2.7）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] window_date 非 date/Timestamp->ValueError；CH 查询异常->fail-open 返回空行（runner 同契约：数据为空->空面板）；symbol 白名单外行->剔除不抛
# [TESTS] tests/pf_core/test_event_sentiment_adapter.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-08-25"
# ---

"""
D_PORTFOLIO_CORE — 事件策略情绪分 runner 契约适配层（BTRUN §3.1 契约缺口接线）。

背景：C1 runner（StrategyRunner）信号契约=合成后标量 ``{symbol: float}``，而
eventdriven-sleeve 要求富负载 ``{symbol: {"event": ...}}``（BTRUN_report §3.1 实证
标量信号下返回空权重）；STR-EVENT-001 跳过根因=情绪分无源（§3.3），D4SENT 已把
规则法情绪分回填 c1_market.news_sentiment_window（19,756 行/4,857 标的/120 窗口日）。
本模块是两者之间的适配层，落点对齐 StrategyRunner 输出契约（``(data, weight_panel)``
二元组中的 weight_panel 段），接线位 = 回测跑批脚本在 load_history 之后、
DefaultBacktestEngine.run 之前调用 ``build_event_weight_panel`` 产面板。

字段映射裁定（数据源可得性边界，留痕）：
  - sentiment_score = sentiment_index（带号 [-1,1]，D4SENT 消费契约）
  - surprise_direction = +1.0（方向由带号情绪分承载：正→入池，负→利空剔除，
    对齐"A股不能做空，利空只能剔除/回避"不变量）
  - class_ = "news"（事件六类分类管道未闭环 #ARCH-NLP-PIPELINE-001；未注册类
    EVENT_CLASS_WEIGHT 默认 1.0 中性权重，不虚报事件类型）
  - decay_stage_factor=1.0（rising，事件次日）/ extreme_reaction_modifier=1.0 /
    day0_reaction=0.0（分钟级反应负载不喂）

SSoT: BTRUN_report §3.1/§3.3 + D4SENT_report 消费契约 + 26号备忘 §2.5/§2.7

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: trade_date 参数
#   fields: 参数 trade_date，类型注解 datetime.date | pd.Timestamp
#   code: event_sentiment_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: rows 参数
#   fields: 参数 rows，类型注解 Sequence[SentimentRow]
#   code: event_sentiment_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: event_class 参数
#   fields: 参数 event_class（无注解）
#   code: event_sentiment_adapter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dates 参数
#   fields: 参数 dates，类型注解 Sequence[pd.Timestamp]
#   code: event_sentiment_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SentimentWindowSource
#   name_en: SentimentWindowSource
#   intro: 情绪窗口数据源协议（生产=ClickHouseSentimentWindowSource，测试=fake 注入）。
#   desc: 情绪窗口数据源协议（生产=ClickHouseSentimentWindowSource，测试=fake 注入）。；公共方法（定义序）: fetch；源码 L175-L178
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② signal_window_date
#   name_en: signal_window_date
#   intro: 交易日 T → 其消费的夜间窗 window_date=T-1（自然日，nightly_window 既有口径）。
#   desc: 交易日 T → 其消费的夜间窗 window_date=T-1（自然日，nightly_window 既有口径）。 PIT 铁律：窗口 [T-1 18:00, T 08:00)…；源码 L181-L193
#   inputs: trade_date
#   outputs: datetime.date
# - id: A3
#   name_zh: ③ sentiment_to_event_payload
#   name_en: sentiment_to_event_payload
#   intro: 情绪行 → eventdriven-sleeve 富负载契约 ``{plain_symbol: {"event": {…
#   desc: 情绪行 → eventdriven-sleeve 富负载契约 ``{plain_symbol: {"event": {...}}}``。 event 负载键与 EventReco…；源码 L201-L225
#   inputs: rows event_class
#   outputs: dict[str, dict[str, Any]]
# - id: A4
#   name_zh: ④ ClickHouseSentimentWindowSource
#   name_en: ClickHouseSentimentWindowSource
#   intro: SentimentWindowSource 默认实现——c1_market.news_sentiment_window…
#   desc: SentimentWindowSource 默认实现——c1_market.news_sentiment_window 薄查询。 lazy import ch_reader：纯函…；公共方法（定义序）: fetch,…
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ build_event_weight_panel
#   name_en: build_event_weight_panel
#   intro: 逐交易日组装事件情绪权重面板（对齐 StrategyRunner._build_weight_panel 输出契约）。
#   desc: 逐交易日组装事件情绪权重面板（对齐 StrategyRunner._build_weight_panel 输出契约）。 每交易日 T：source.fetch(window_da…；源码 L294-L375
#   inputs: dates universe source strategy top_n max_single exclude event_class
#   outputs: pd.DataFrame
# - id: A6
#   name_zh: ⑥ EventSentimentAdapter
#   name_en: EventSentimentAdapter
#   intro: 事件策略情绪分适配层门面（runner 契约接线位）。
#   desc: 事件策略情绪分适配层门面（runner 契约接线位）。 持有 source/strategy/参数，一次装配多次产出权重面板；等价于 build_event_weight_pan…；公共方法（定义序）: build_w…
#   inputs: source strategy top_n max_single event_class
#   outputs: 返回值
#   （注：A6 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: datetime.date
#   name_en: datetime.date
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件策略回测跑批（.runtime 施工件）；zephyr.pf_core.strategy_engine（lazy re-export）
# - id: O2
#   name_zh: dict[str, dict[str, Any]]
#   name_en: dict[str, dict[str, Any]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件策略回测跑批（.runtime 施工件）；zephyr.pf_core.strategy_engine（lazy re-export）
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
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Final, Protocol, Sequence, runtime_checkable

import pandas as pd

_logger = logging.getLogger(__name__)

DEFAULT_EVENT_CLASS: Final = "news"  # 未注册类→EVENT_CLASS_WEIGHT 默认 1.0 中性（六类无源不虚报）
DEFAULT_TOP_N: Final = 10  # eventdriven-sleeve 策略默认
DEFAULT_MAX_SINGLE: Final = 0.10  # eventdriven-sleeve 策略默认

_TARGET_TABLE: Final = "c1_market.news_sentiment_window"
_SYMBOL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9.]{1,20}$")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，同 event_score 约定）
_SQL_SENTIMENT = (
    "SELECT symbol, sentiment_index, positive_count, negative_count, neutral_count, total_count, window_date "
    f"FROM {_TARGET_TABLE} WHERE scope='symbol' AND window_date = '{{window_date}}'"
)


@dataclass(frozen=True, slots=True)
class SentimentRow:
    """news_sentiment_window symbol 级行（适配层输入契约）。"""

    symbol: str  # canonical（"600519.SH"）或纯数字（"600519"）
    sentiment_index: float
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    total_count: int = 0
    window_date: datetime.date | None = None  # 记录归属窗口日（PIT 护栏判据；None=源未携带，放行兼容）


@runtime_checkable
class SentimentWindowSource(Protocol):
    """情绪窗口数据源协议（生产=ClickHouseSentimentWindowSource，测试=fake 注入）。"""

    def fetch(self, window_date: datetime.date, symbols: Sequence[str] | None = None) -> list[SentimentRow]: ...


def signal_window_date(trade_date: datetime.date | pd.Timestamp) -> datetime.date:
    """交易日 T → 其消费的夜间窗 window_date=T-1（自然日，nightly_window 既有口径）。

    PIT 铁律：窗口 [T-1 18:00, T 08:00) 收盘于 T 开盘前，无未来函数；
    周一 T 的窗=周日 18:00 起（window_date=周日），跨周末新闻由该窗覆盖。
    """
    if isinstance(trade_date, pd.Timestamp):
        d = trade_date.date()
    elif isinstance(trade_date, datetime.date):
        d = trade_date
    else:
        raise ValueError(f"signal_window_date: trade_date 须为 date/Timestamp，实际 {type(trade_date).__name__}")
    return d - datetime.timedelta(days=1)


def _strip_suffix(symbol: str) -> str:
    """canonical "600519.SH" → 纯数字 "600519"（与 load_history 面板 symbol 同源）。"""
    return symbol.split(".")[0] if "." in symbol else symbol


def sentiment_to_event_payload(
    rows: Sequence[SentimentRow],
    *,
    event_class: str = DEFAULT_EVENT_CLASS,
) -> dict[str, dict[str, Any]]:
    """情绪行 → eventdriven-sleeve 富负载契约 ``{plain_symbol: {"event": {...}}}``。

    event 负载键与 EventRecord 字段对齐（symbol 由策略侧注入，此处不重复键）；
    带号 sentiment_index 直接映射 sentiment_score，方向由符号承载。
    """
    payload: dict[str, dict[str, Any]] = {}
    for r in rows:
        if not isinstance(r.symbol, str) or not r.symbol:
            continue
        payload[_strip_suffix(r.symbol)] = {
            "event": {
                "class_": event_class,
                "surprise_direction": 1.0,
                "sentiment_score": float(r.sentiment_index),
                "decay_stage_factor": 1.0,
                "extreme_reaction_modifier": 1.0,
                "day0_reaction": 0.0,
            }
        }
    return payload


class ClickHouseSentimentWindowSource:
    """SentimentWindowSource 默认实现——c1_market.news_sentiment_window 薄查询。

    lazy import ch_reader：纯函数测试路径零 CH 依赖（同 event_score 约定）。
    ERROR_CONTRACT：查询异常 fail-open 返回空行（runner 数据为空->空面板同契约）。
    """

    def fetch(self, window_date: datetime.date, symbols: Sequence[str] | None = None) -> list[SentimentRow]:
        if not isinstance(window_date, datetime.date) or isinstance(window_date, datetime.datetime):
            raise ValueError(
                f"ClickHouseSentimentWindowSource.fetch: window_date 须为 date，实际 {type(window_date).__name__}"
            )
        from zephyr.data import ch_reader

        try:
            tsv = ch_reader.query(_SQL_SENTIMENT.format(window_date=window_date.isoformat()))
        except Exception as exc:  # noqa: BLE001 — fail-open 空行（runner 空数据契约）
            _logger.warning("news_sentiment_window 查询异常，降级空行（fail-open）: %s", exc)
            return []
        rows: list[SentimentRow] = []
        for line in (tsv or "").strip().splitlines():
            parts = line.split("\t")
            if len(parts) != 7:
                continue
            try:
                row = self.parse_row(tuple(parts))
            except (ValueError, TypeError):
                continue
            if not self.valid_symbol(row.symbol):
                continue
            if symbols is not None and _strip_suffix(row.symbol) not in {_strip_suffix(s) for s in symbols}:
                continue
            rows.append(row)
        return rows

    @staticmethod
    def parse_row(raw: tuple) -> SentimentRow:
        """TSV 行（str 元组）→ SentimentRow；数值转换失败抛 ValueError（调用方剔除）。

        6 列=（symbol, sentiment_index, 正/负/中/总条数）旧契约（window_date 缺省 None）；
        7 列追加 window_date（ISO 字符串或 date，PIT 护栏判据）。
        """
        win: datetime.date | None = None
        if len(raw) >= 7 and raw[6] not in (None, ""):
            if isinstance(raw[6], datetime.datetime):
                win = raw[6].date()
            elif isinstance(raw[6], datetime.date):
                win = raw[6]
            else:
                win = datetime.date.fromisoformat(str(raw[6]))
        return SentimentRow(
            symbol=str(raw[0]),
            sentiment_index=float(raw[1]),
            positive_count=int(float(raw[2])),
            negative_count=int(float(raw[3])),
            neutral_count=int(float(raw[4])),
            total_count=int(float(raw[5])),
            window_date=win,
        )

    @staticmethod
    def valid_symbol(symbol: str) -> bool:
        """symbol 白名单校验（防注入，同 event_score._SYMBOL_RE 约定）。"""
        return bool(_SYMBOL_RE.match(symbol))


def build_event_weight_panel(
    dates: Sequence[pd.Timestamp],
    universe: Sequence[str],
    *,
    source: SentimentWindowSource | None = None,
    strategy: Any | None = None,
    top_n: int = DEFAULT_TOP_N,
    max_single: float = DEFAULT_MAX_SINGLE,
    exclude: Callable[[pd.Timestamp], set[str]] | None = None,
    event_class: str = DEFAULT_EVENT_CLASS,
) -> pd.DataFrame:
    """逐交易日组装事件情绪权重面板（对齐 StrategyRunner._build_weight_panel 输出契约）。

    每交易日 T：source.fetch(window_date=T-1) → PIT 护栏（window_date>T-1 记录硬剔除）
    → 富负载 → 过滤（universe∩exclude）→ strategy.generate_target_weights → 面板行。
    空窗/零入选日该行保持全零——
    DefaultBacktestEngine._normalize_day_signals 仅取 >0 分量，全零行=当日不下单、
    沿用既有持仓（hold），与 runner 非调仓日语义一致（引擎实测契约）。

    Args:
        dates: 交易日序列（pd.Timestamp，通常取 load_history 面板 index）。
        universe: 纯数字代码标的列表（面板列，与 load_history 同源）。
        source: 情绪源（None=ClickHouse 默认实现）。
        strategy: 事件策略实例（None=EventDrivenSleeveStrategy()）。
        top_n / max_single: 透传策略 constraints（默认=策略默认值）。
        exclude: 调仓日剔除集合钩子（如 ST PIT 排除），None=不排除。
        event_class: EventRecord.class_（默认 "news"，未注册类中性权重 1.0）。

    Returns:
        DataFrame(date×universe) 目标权重面板，可直接喂 DefaultBacktestEngine.run。
    """
    if strategy is None:
        from zephyr.pf_core.strategies.event_driven_sleeve_strategy import (
            EventDrivenSleeveStrategy,
        )

        strategy = EventDrivenSleeveStrategy()
    if source is None:
        source = ClickHouseSentimentWindowSource()

    idx = pd.DatetimeIndex(pd.to_datetime(list(dates)))
    cols = [str(s) for s in universe]
    panel = pd.DataFrame(0.0, index=idx, columns=cols)
    uni_set = set(cols)

    for d in idx:
        win_date = signal_window_date(d)
        rows = source.fetch(win_date)
        if not rows:
            continue
        # PIT 防未来函数护栏：T 日决策只消费 window_date ≤ T-1 的记录；
        # window_date 缺失（None）= 源未携带归属日，放行兼容（fetch 点查询本身已按 T-1 取窗）
        consumable: list[SentimentRow] = []
        violations = 0
        for r in rows:
            if r.window_date is not None and r.window_date > win_date:
                violations += 1
                continue
            consumable.append(r)
        if violations:
            _logger.warning(
                "PIT 护栏：交易日 %s 剔除 %d 条 window_date > T-1(%s) 情绪记录（防未来函数，未消费）",
                d.date(),
                violations,
                win_date,
            )
        if not consumable:
            continue
        payload = sentiment_to_event_payload(consumable, event_class=event_class)
        excluded = exclude(d) if exclude is not None else set()
        tradable = [s for s in payload if s in uni_set and s not in excluded]
        if not tradable:
            continue
        weights = strategy.generate_target_weights(
            universe=tradable,
            signals={s: payload[s] for s in tradable},
            constraints={"top_n": top_n, "max_single": max_single},
        )
        for sym, w in weights.items():
            panel.loc[d, sym] = w

    return panel.fillna(0.0)


class EventSentimentAdapter:
    """事件策略情绪分适配层门面（runner 契约接线位）。

    持有 source/strategy/参数，一次装配多次产出权重面板；等价于
    build_event_weight_panel 的对象化封装，供跑批脚本与后续盘中链路复用。
    """

    def __init__(
        self,
        *,
        source: SentimentWindowSource | None = None,
        strategy: Any | None = None,
        top_n: int = DEFAULT_TOP_N,
        max_single: float = DEFAULT_MAX_SINGLE,
        event_class: str = DEFAULT_EVENT_CLASS,
    ) -> None:
        self._source = source
        self._strategy = strategy
        self._top_n = top_n
        self._max_single = max_single
        self._event_class = event_class

    def build_weight_panel(
        self,
        dates: Sequence[pd.Timestamp],
        universe: Sequence[str],
        *,
        exclude: Callable[[pd.Timestamp], set[str]] | None = None,
    ) -> pd.DataFrame:
        """见 build_event_weight_panel（exclude 之外的参数取自装配）。"""
        return build_event_weight_panel(
            dates,
            universe,
            source=self._source,
            strategy=self._strategy,
            top_n=self._top_n,
            max_single=self._max_single,
            exclude=exclude,
            event_class=self._event_class,
        )


__all__: Final = [
    "DEFAULT_EVENT_CLASS",
    "DEFAULT_MAX_SINGLE",
    "DEFAULT_TOP_N",
    "ClickHouseSentimentWindowSource",
    "EventSentimentAdapter",
    "SentimentRow",
    "SentimentWindowSource",
    "build_event_weight_panel",
    "sentiment_to_event_payload",
    "signal_window_date",
]
