# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.daban_load_producer
# [DOMAIN] D_EXECUTION_CORE
# [DEPENDENCIES] pandas; zephyr.data.ch_reader（lazy，只读）; zephyr.data.ch_writer（lazy，落表）; zephyr.data.implementations.daban_board_event_deriver（collect_derived_events，回填/验证只读）; zephyr.data.table_registry（表真源，lazy）
# [CONSUMERS] 日频 reconciler 链（事件触发调 run_daily_batch+persist，tasks.yaml 接线=主会话待办）; zephyr.pf_core.strategies.daban_sleeve_strategy（**默认消费方**：无注入 load_source 时经其 _PersistedDabanLoadSource 走 DatabaseService PIT 真读本表；ClickHouseDabanEngineLoadSource 为 ch_reader 备选通道）; lane A framework_composer（build_weight_panel_for_dates 产面板路由）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 事件驱动非周期：本模块是**批产生产者**，由上游 reconciler（daban_board_event 派生任务落库后）触发的 run_daily_batch 调用，MUST NOT 自带 cron/Timer/sleep-loop；生成器纯函数路径零 datetime.now()/time.time()（RULE-SCHEMA-TZ——ingest_ts 由 DDL 侧 now() DEFAULT 承载，Python 侧不取时钟，elapsed_sec 恒 0.0）；真源唯一：负载字段口径以 schemas/categories/market/market_daban_engine_load.py DDL 为唯一真源，LOAD_INSERT_COLUMNS 与其 INSERT_COLUMNS 严格同序 21 列；可产字段真实映射（float_market_cap 真连 stock_indicator.circ_mv 万元×1e4）、不可产字段**省略**（交引擎 dataclass 中性默认，禁拍假值冒充真值）并逐字段留痕 derived_fields；PIT：本表 trade_date=打板事件日（=决策日 T 的 T-1），消费侧（本模块 ClickHouseDabanEngineLoadSource 与策略侧 daban_sleeve_strategy._PersistedDabanLoadSource）只回 trade_date < as_of 的最新事件日分区；CH 全程经 ch_reader/ch_writer（禁裸 SQL 散落，_SQL_* 常量集中）；selector 资格门不喂（见 row→payload 契约在策略侧，本模块只产负载行不产引擎负载键）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 事件窗口倒置/日期非法->ValueError（透传 deriver 契约）；空事件日->run_daily_batch 返回空 rows 的 FetchResult + logger.warning（fail-visible，非静默）；CH 读源查询异常->fail-open 空（ClickHouseDabanEngineLoadSource/DabanBoardEventSource 同 event adapter 契约）；persist 落表经 ch_writer.write_result（error 非 None 返回 False，不抛）
# [TESTS] tests/ex_core/test_daban_load_producer.py
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""D_EXECUTION_CORE — daban 四引擎应用层负载日频批产生产者（T3⑧ / 挖矿 LUE-1 治本）。

背景（挖矿 LUE-1 实证）：
    daban-sleeve 在 fw-tdm-current 挂 0.0945 权重，但其消费的四引擎
    （selector/youzi/quant/fusion_context）负载**无日频批产源**——权重有、输入没有，
    0.0945 与 T1A-1 死成员同根空转。地基（daban_board_event 派生表 + stk_limit 精确
    join）已由裁定#257⑤ 接通；本模块是其上的**应用层负载批产真源**：
    日频生产者从 daban_board_event（事件日口径）派生四引擎可产字段，落
    c1_market.daban_engine_load；daban_sleeve_strategy 从本表 PIT 真读。
    裁定#257⑥ 曾判应用层"挂起不建"，经 Owner 2026-09-16 令"清单里还没开工的、设计态
    的全线施工，不留待裁定内容"解除挂起、落地本模块。

可产字段（真实映射，见 events_to_load_rows）：
    consec_limit / open_board_count / first_touch_time / seal_amount(=seal_amount_proxy) /
    float_market_cap(=stock_indicator.circ_mv 万元×1e4 折元，经 fetch_float_cap_map 真连) /
    stock_change_pct(=close/pre_close-1) / close_price / limit_up_price / is_one_word /
    board / st_flag / seal_time_minutes(=first_touch 折算 09:30 起分钟，午间休市扣除) /
    sector_limit_up_count(=当日同 board 真封板家数，窗口自产) /
    market_limit_up_count(=当日全市场真封板家数，窗口自产)。
    注：float_market_cap 是挖矿 LUE-1 实证可产真字段——喂 youzi 封流比（seal_amount/
    float_market_cap，封单质量 20 分因子）与 quant 资金分母；此前欠产使封单质量恒 0 分、
    融合分压在"中性"下（真数据复验仅 1.4% 封板事件越阈），本字段补齐即治本、0.0945 归位。
不可产字段（省略，交引擎 dataclass 中性默认，不拍假值；derived_fields 标 default）：
    selector 侧机构输入（target_price/fundamental_score/corr_with_market/turnover_rate/
    large_order_ratio/catalyst_strength——本事件源无此维度，喂默认会
    使 overall<45→"回避"系统性清零整条 sleeve，故 row→payload 契约侧**不喂 selector
    门**，见 daban_sleeve_strategy 文档）；youzi 竞价因子（auction_rise_pct/
    auction_volume_ratio）；quant 动量 z 分/资金流/技术分/风险分。
    market_breadth_ratio / market_change_pct —— 有快照则真实、否则 default（best-effort）。

链路与边界：
    事件触发：上游 reconciler（daban_board_event 派生任务）落库后调
    run_daily_batch(event_day)→persist(result)（tasks.yaml 接线=主会话待办，见交付报告）。
    生成器零时钟：纯函数无 now()；本表 ingest_ts 由 DDL `DEFAULT now()` 侧承载。
    读写分离：读经 ch_reader（含派生回填源 collect_derived_events，只读 SELECT），
    写经 ch_writer.write_result（FetchResult），CH 不可达时由其本地落盘兜底（裁定
    #ARCH-CH-013），本会话为只读验证不触发真写。

SSoT: docs/_working/full-auto-chain/S11_assembled_backtest/nodes/limit_up_event_load_mining.md LUE-1/2/3
     + schemas/categories/market/market_daban_engine_load.py（表结构唯一真源）
     + docs/02.../21_stock_selection_engine.md §3.5/§3.6（四引擎负载契约）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: events 参数
#   fields: 参数 events，类型注解 Sequence[DabanBoardEvent]
#   code: daban_load_producer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: market_context 参数
#   fields: 参数 market_context，类型注解 Mapping[str, Mapping[str, float]] | None
#   code: daban_load_producer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: event_day / as_of_date 参数
#   fields: 参数 event_day / as_of_date，类型注解 date | str
#   code: daban_load_producer.py 公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① seal_time_minutes_from_touch
#   name_en: seal_time_minutes_from_touch
#   intro: 首触时刻 HH:MM:SS → 封板分钟数（09:30 起，午间 11:30-13:00 休市扣除）。
#   desc: 首触时刻 HH:MM:SS → 封板分钟数（09:30 起，午间休市扣除）；None→None（default 留痕）。
# - id: A2
#   name_zh: ② stock_change_pct
#   name_en: stock_change_pct
#   intro: (close/pre_close−1)×100；缺昨收/非正→None（default 留痕）。
#   desc: (close/pre_close−1)×100；pre_close None/<=0 或 close None → None。
# - id: A3
#   name_zh: ③ events_to_load_rows
#   name_en: events_to_load_rows
#   intro: DabanBoardEvent 列表 → daban_engine_load 负载行 dict 列表（真封板口径自产板块/市场家数 + derived_fields 留痕）。
#   desc: 逐事件映射为 21 列负载行；sector/market 真封板家数按事件批自窗聚合；市场宽度/大盘涨幅按 market_context 注入、流通市值按 cap_map 注入（均缺则 default）。
# - id: A4
#   name_zh: ④ load_rows_to_tuples
#   name_en: load_rows_to_tuples
#   intro: 负载行 dict → 与 LOAD_INSERT_COLUMNS 同序的 tuple 列表（derived_fields JSON 序列化）。
#   desc: 输出供 FetchResult.rows；缺列以 None 占位（Nullable 列 \N）。
# - id: A5
#   name_zh: ⑤ run_daily_batch
#   name_en: run_daily_batch
#   intro: 单日事件 → FetchResult（目标表 daban_engine_load）；空事件日 warning + 空 rows。
#   desc: 编排读源→events_to_load_rows→tuples→FetchResult；不触发写，不调时钟。
# - id: A6
#   name_zh: ⑥ persist
#   name_en: persist
#   intro: FetchResult → ch_writer.write_result 落 ClickHouse。
#   desc: 生产落表入口（本只读验证会话不调用）；write_result 内部处理列过滤/MATERIALIZED 排除。
# - id: A7
#   name_zh: ⑦ ClickHouseDabanBoardEventSource / DerivedDabanBoardEventSource
#   name_en: ClickHouseDabanBoardEventSource / DerivedDabanBoardEventSource
#   intro: 事件源协议与两实现——生产读 daban_board_event 表；回填/验证经 collect_derived_events 只读推导。
#   desc: DabanEventSource.fetch_events(start,end)->list[DabanBoardEvent]；表源查询异常 fail-open 空。
# - id: A8
#   name_zh: ⑧ ClickHouseDabanEngineLoadSource
#   name_en: ClickHouseDabanEngineLoadSource
#   intro: 消费侧 PIT 读源——fetch_load(as_of) 回 trade_date<as_of 的最新事件日负载行。
#   desc: 先解析 max(trade_date)<as_of，再取该分区行；查询异常 fail-open 空（策略侧据此告警 skipped）。
# - id: A9
#   name_zh: ⑨ fetch_float_cap_map
#   name_en: fetch_float_cap_map
#   intro: 流通市值真连接（只读）——stock_indicator.circ_mv（万元）×1e4 折元 → {(day,symbol):元}。
#   desc: 挖矿 LUE-1 实证可产真字段（封单质量/资金因子分母）；reader 注入位（None=lazy ch_reader.query）；查询异常 fail-open 空 map（字段降 default）。
# 层: 输出
# - id: O1
#   name_zh: list[dict] / FetchResult / pd.DataFrame
#   name_en: producer outputs
#   intro: 负载行 dict 列表 / FetchResult / （策略侧）日期×标的权重面板
#   downstream: c1_market.daban_engine_load（persist）; daban_sleeve_strategy（fetch_load 消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A3
# I2 --> A3
# I1 --> A1
# I1 --> A2
# A1 --> A3
# A2 --> A3
# A9 --> A3
# A3 --> A4
# A4 --> A5
# A7 --> A5
# A5 --> A6
# A5 --> O1
# A8 --> O1
"""

from __future__ import annotations

import datetime
import json
import logging
import re
from typing import TYPE_CHECKING, Any, Final, Mapping, Protocol, Sequence, runtime_checkable

if TYPE_CHECKING:
    from zephyr.data.implementations.daban_board_event_deriver import DabanBoardEvent
    from zephyr.data.provider_base import FetchResult

_logger = logging.getLogger(__name__)

#: 目标表（消费表结构真源 = schemas/categories/market/market_daban_engine_load.py）
_TARGET_TABLE: Final = "c1_market.daban_engine_load"
CATEGORY_ID: Final = "market_daban_engine_load"
_EVENT_TABLE: Final = "c1_market.daban_board_event"
LOAD_VERSION: Final = "v1"
_DATA_SOURCE: Final = "daban_board_event_derived"

#: 事件日下限哨兵（沪深交易所开市日）。CH 对空 Date 列取 max() 回 1970-01-01
#: （或 0000-00-00，取决于版本），早于此一律判"无分区"，不得被误读成陈旧回退分区。
#: 消费侧（daban_sleeve_strategy）共用本常量，禁各自另写日期字面量。
MIN_EVENT_DATE: Final = datetime.date(1990, 12, 19)

#: INSERT 列序——与 DDL INSERT_COLUMNS 严格同序 21 列（不含 MATERIALIZED exchange/
#: symbol_canonical 与 DEFAULT ingest_ts；ch_writer.write_result 自动过滤 MATERIALIZED）。
LOAD_INSERT_COLUMNS: Final = (
    "trade_date",
    "symbol",
    "board",
    "st_flag",
    "consec_limit",
    "open_board_count",
    "first_touch_time",
    "seal_time_minutes",
    "seal_amount",
    "float_market_cap",
    "stock_change_pct",
    "close_price",
    "limit_up_price",
    "is_one_word",
    "sector_limit_up_count",
    "market_limit_up_count",
    "market_breadth_ratio",
    "market_change_pct",
    "derived_fields",
    "load_version",
    "data_source",
)

# 连续竞价时段口径（分钟-of-day）：09:30 开盘、11:30 午收、13:00 午开、15:00 收。
_OPEN_MIN: Final = 9 * 60 + 30  # 570
_MORNING_END_MIN: Final = 11 * 60 + 30  # 690
_AFTERNOON_START_MIN: Final = 13 * 60  # 780
_LUNCH_MIN: Final = _AFTERNOON_START_MIN - _MORNING_END_MIN  # 90
_MORNING_SPAN_MIN: Final = _MORNING_END_MIN - _OPEN_MIN  # 120
_FULL_SESSION_MIN: Final = _MORNING_SPAN_MIN * 2  # 240（连续竞价总分钟，下午上限）

_SYMBOL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9.]{1,20}$")
_HHMMSS_RE: Final[re.Pattern[str]] = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*$")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，同 event_sentiment_adapter 约定）
_SQL_EVENTS_BY_RANGE = (
    "SELECT trade_date, symbol, board, st_flag, consec_limit, open_board_count, "
    "first_touch_time, seal_amount_proxy, close, limit_up_price, is_one_word, pre_close "
    f"FROM {_EVENT_TABLE} "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}')"
)
# 消费侧 PIT：先定位 < as_of 的最新事件日（决策日 T 只用前一交易日，禁未来函数）
_SQL_LOAD_MAX_EVENT_DATE = (
    f"SELECT max(trade_date) FROM {_TARGET_TABLE} WHERE trade_date < toDate('{{as_of}}')"
)
_SQL_LOAD_ROWS_BY_DATE = (
    "SELECT trade_date, symbol, board, st_flag, consec_limit, open_board_count, "
    "first_touch_time, seal_time_minutes, seal_amount, float_market_cap, stock_change_pct, "
    "close_price, limit_up_price, is_one_word, sector_limit_up_count, market_limit_up_count, "
    "market_breadth_ratio, market_change_pct, derived_fields, load_version, data_source "
    f"FROM {_TARGET_TABLE} WHERE trade_date = toDate('{{event_date}}')"
)

#: 流通市值只读维度源（挖矿 LUE-1 可产真字段：stock_indicator.circ_mv，2015+ 全史）。
#: circ_mv 口径=万元（实证 600519 total_mv≈1.59e8 万元≈1.59 万亿），×1e4 折元对齐引擎契约(元)。
_CAP_TABLE: Final = "c1_market.stock_indicator"
_WAN_TO_YUAN: Final = 1e4
_SQL_CAP_BY_DAY_SYMBOLS = (
    "SELECT toString(trade_date), symbol, circ_mv "
    f"FROM {_CAP_TABLE} "
    "WHERE trade_date IN ({dates}) AND symbol IN ({symbols}) AND circ_mv IS NOT NULL"
)


# ---------------------------------------------------------------------------
# 纯函数层（零时钟、零 IO）
# ---------------------------------------------------------------------------


def _parse_hhmmss_minutes(value: str | None) -> int | None:
    """'HH:MM:SS'/'HH:MM'/datetime → 当日分钟数（minutes-of-day）；不可解析→None。"""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.hour * 60 + value.minute
    m = _HHMMSS_RE.search(str(value))
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    return hour * 60 + minute


def seal_time_minutes_from_touch(first_touch_time: str | None) -> int | None:
    """首触时刻 → 封板分钟数（从开盘 09:30 起，午间 11:30-13:00 休市扣除）。

    口径（A 股连续竞价）：
        - <=09:30（含 09:25 集合竞价一字板）→ 0（开盘即封=最强）。
        - 09:30-11:30 → mod − 09:30（0..120）。
        - 11:30-13:00（午休，理论无成交）→ 120（钳到午收）。
        - 13:00-15:00 → (mod − 09:30) − 90（扣午休），封顶 240。
    无首触时刻（分钟数据缺）→ None（derived_fields 标 default，非拍 0 冒充早封）。
    """
    mod = _parse_hhmmss_minutes(first_touch_time)
    if mod is None:
        return None
    if mod <= _OPEN_MIN:
        return 0
    if mod <= _MORNING_END_MIN:
        return mod - _OPEN_MIN
    if mod < _AFTERNOON_START_MIN:
        return _MORNING_SPAN_MIN
    return min((mod - _OPEN_MIN) - _LUNCH_MIN, _FULL_SESSION_MIN)


def stock_change_pct(close: float | None, pre_close: float | None) -> float | None:
    """个股当日涨幅（%）=(close/pre_close−1)×100；缺值/昨收非正→None（default 留痕）。"""
    if close is None or pre_close is None or pre_close <= 0:
        return None
    return (close / pre_close - 1.0) * 100.0


def _iso_day(value: Any) -> str:
    """归一事件日为 ISO 'YYYY-MM-DD' 字符串（CH Date 驱动可能回 date/datetime/str）。"""
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)[:10]


def events_to_load_rows(
    events: Sequence["DabanBoardEvent"],
    *,
    market_context: Mapping[str, Mapping[str, float]] | None = None,
    cap_map: Mapping[tuple[str, str], float] | None = None,
) -> list[dict[str, Any]]:
    """打板事件列表 → daban_engine_load 负载行 dict 列表（真封板口径 + derived_fields 留痕）。

    Args:
        events: DabanBoardEvent（derive_daily_events/enrich_* 产物，全为 touched 事件）。
        market_context: {event_day_iso: {"breadth_ratio": float, "change_pct": float}}
            ——市场宽度/大盘涨幅注入位（缺则该字段 default）。sector/market 真封板家数
            不依赖此参数，由本函数按事件批自窗聚合（真实字段）。
        cap_map: {(event_day_iso, symbol): float_market_cap_元}——流通市值真连接入位
            （由 fetch_float_cap_map 经 stock_indicator.circ_mv 万元×1e4 折元，缺则该字段
            default）。喂 youzi 封流比（seal_amount/cap，封单质量 20 分因子）/quant 资金。

    Returns:
        负载行 dict 列表（键=LOAD_INSERT_COLUMNS；行序=输入事件序，调用方可自行排序）。
        未派生的不可产字段以 None 占位（Nullable 列写 \\N），并计入 derived_fields。
    """
    # 1) 窗口自产：真封板（close_sealed）家数——市场级按事件日、板块级按（事件日, board）
    market_sealed: dict[str, int] = {}
    sector_sealed: dict[tuple[str, str], int] = {}
    for e in events:
        if getattr(e, "close_sealed", 0):
            day = _iso_day(e.trade_date)
            market_sealed[day] = market_sealed.get(day, 0) + 1
            key = (day, str(e.board))
            sector_sealed[key] = sector_sealed.get(key, 0) + 1

    ctx = market_context or {}
    rows: list[dict[str, Any]] = []
    for e in events:
        day = _iso_day(e.trade_date)
        open_board = getattr(e, "open_board_count", None)
        first_touch = getattr(e, "first_touch_time", None)
        seal_minutes = seal_time_minutes_from_touch(first_touch)
        seal_amount = getattr(e, "seal_amount_proxy", None)
        pct = stock_change_pct(getattr(e, "close", None), getattr(e, "pre_close", None))
        day_ctx = ctx.get(day, {}) if isinstance(ctx, dict) else {}
        breadth = day_ctx.get("breadth_ratio")
        mkt_pct = day_ctx.get("change_pct")
        caps = cap_map or {}
        cap = caps.get((day, str(e.symbol))) if isinstance(caps, dict) else None

        derived = {
            "board": "real",
            "st_flag": "real",
            "consec_limit": "real",
            "is_one_word": "real",
            "limit_up_price": "real",
            "open_board_count": "real" if open_board is not None else "default",
            "first_touch_time": "real" if first_touch is not None else "default",
            "seal_time_minutes": "real" if seal_minutes is not None else "default",
            "seal_amount": "real" if seal_amount is not None else "default",
            "float_market_cap": "real" if cap is not None else "default",
            "stock_change_pct": "real" if pct is not None else "default",
            "close_price": "real" if getattr(e, "close", None) is not None else "default",
            "sector_limit_up_count": "real",
            "market_limit_up_count": "real",
            "market_breadth_ratio": "real" if breadth is not None else "default",
            "market_change_pct": "real" if mkt_pct is not None else "default",
        }
        rows.append(
            {
                "trade_date": day,
                "symbol": str(e.symbol),
                "board": str(e.board),
                "st_flag": int(getattr(e, "st_flag", 0) or 0),
                "consec_limit": int(getattr(e, "consec_limit", 0) or 0),
                "open_board_count": None if open_board is None else int(open_board),
                "first_touch_time": None if first_touch is None else str(first_touch),
                "seal_time_minutes": seal_minutes,
                "seal_amount": None if seal_amount is None else float(seal_amount),
                "float_market_cap": None if cap is None else float(cap),
                "stock_change_pct": pct,
                "close_price": _maybe_float(getattr(e, "close", None)),
                "limit_up_price": float(getattr(e, "limit_up_price", 0.0) or 0.0),
                "is_one_word": int(getattr(e, "is_one_word", 0) or 0),
                "sector_limit_up_count": sector_sealed.get((day, str(e.board)), 0),
                "market_limit_up_count": market_sealed.get(day, 0),
                "market_breadth_ratio": None if breadth is None else float(breadth),
                "market_change_pct": None if mkt_pct is None else float(mkt_pct),
                "derived_fields": json.dumps(derived, ensure_ascii=False, sort_keys=True),
                "load_version": LOAD_VERSION,
                "data_source": _DATA_SOURCE,
            }
        )
    return rows


def _maybe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def load_rows_to_tuples(rows: Sequence[Mapping[str, Any]]) -> list[tuple]:
    """负载行 dict → 与 LOAD_INSERT_COLUMNS 同序的 tuple 列表（供 FetchResult.rows）。"""
    out: list[tuple] = []
    for row in rows:
        out.append(tuple(row.get(col) for col in LOAD_INSERT_COLUMNS))
    return out


# ---------------------------------------------------------------------------
# 事件源层（生产=读 daban_board_event 表；回填/验证=collect_derived_events 只读推导）
# ---------------------------------------------------------------------------


@runtime_checkable
class DabanEventSource(Protocol):
    """打板事件源协议（生产=表源，回填/验证=派生源，测试=fake 注入）。"""

    def fetch_events(self, start: datetime.date, end: datetime.date) -> list["DabanBoardEvent"]: ...


_EVENT_CATEGORY_ID: Final = "market_daban_board_event"  # deriver CATEGORY_ID（表名真源键）


class ClickHouseDabanBoardEventSource:
    """生产事件源——c1_market.daban_board_event 薄查询（表已派生落库后）。

    表名经 table_registry 解析（RULE-SSOT/REGISTRY，禁硬编码表名绕过真源）；
    lazy import ch_reader：纯函数测试路径零 CH 依赖。
    ERROR_CONTRACT：查询异常/品类未注册 fail-open 返回空列表（上游 run_daily_batch warning）。
    """

    def fetch_events(self, start: datetime.date, end: datetime.date) -> list["DabanBoardEvent"]:
        from zephyr.data.implementations.daban_board_event_deriver import DabanBoardEvent
        from zephyr.data.table_registry import get_registry

        try:
            table = get_registry().table(_EVENT_CATEGORY_ID)  # "{database}.{table}"
            sql = _SQL_EVENTS_BY_RANGE.format(start=start.isoformat(), end=end.isoformat())
            if table != _EVENT_TABLE:
                sql = sql.replace(_EVENT_TABLE, table, 1)
            raw = _reader_rows(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open 空（对齐 event adapter 契约）
            _logger.warning("daban_board_event 查询异常，降级空事件（fail-open）: %s", exc)
            return []
        out: list[DabanBoardEvent] = []
        for r in raw:
            try:
                out.append(_row_to_event(DabanBoardEvent, r))
            except (ValueError, TypeError, IndexError):
                continue
        return out


def _tsv_val(raw: Any) -> str | None:
    """TSV 字段归一：\\N/空/None→None，否则 str。"""
    if raw is None:
        return None
    s = str(raw)
    return None if s in ("\\N", "") else s


def _reader_rows(sql: str) -> list[tuple]:
    """经 ch_reader.query(TSV) 取行（12 列事件视图）。"""
    from zephyr.data import ch_reader

    tsv = ch_reader.query(sql)
    rows: list[tuple] = []
    for line in (tsv or "").strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= len(_SQL_EVENT_COLS):
            rows.append(tuple(parts[: len(_SQL_EVENT_COLS)]))
    return rows


_SQL_EVENT_COLS: Final = (
    "trade_date",
    "symbol",
    "board",
    "st_flag",
    "consec_limit",
    "open_board_count",
    "first_touch_time",
    "seal_amount_proxy",
    "close",
    "limit_up_price",
    "is_one_word",
    "pre_close",
)


def _row_to_event(evt_cls: Any, r: Sequence[Any]) -> Any:
    """daban_board_event 行 → DabanBoardEvent（12 列视图，见 _SQL_EVENT_COLS）。

    close_sealed 保守按 1 处理（表落封住口径；炸板行由 collect 派生源真实携带）。
    数值列经 _tsv_val 容错 \\N（ Nullable 列 TSV 表现）。
    """
    loup = _tsv_val(r[9])
    return evt_cls(
        trade_date=_iso_day(r[0]),
        symbol=str(r[1]),
        board=str(r[2]),
        st_flag=int(float(_tsv_val(r[3]) or 0)),
        pre_close=_maybe_float(_tsv_val(r[11])),
        limit_up_price=float(loup) if loup is not None else 0.0,
        open=None,
        high=None,
        low=None,
        close=_maybe_float(_tsv_val(r[8])),
        touched=1,
        close_sealed=1,
        is_one_word=int(float(_tsv_val(r[10]) or 0)),
        first_touch_time=_tsv_val(r[6]),
        open_board_count=(None if _tsv_val(r[5]) is None else int(float(_tsv_val(r[5])))),
        seal_bid_volume=None,
        seal_amount_proxy=_maybe_float(_tsv_val(r[7])),
        consec_limit=int(float(_tsv_val(r[4]) or 0)),
        limit_src="daban_board_event_table",
        data_source=_DATA_SOURCE,
    )


class DerivedDabanBoardEventSource:
    """回填/验证事件源——collect_derived_events 只读推导（表未落/需真数据复验时用）。

    ch_client 惰性构造（None=经 DatabaseService reader 角色），零写库；sleep 注 noop 避免
    回填限速阻塞（deriver tushare 兜底路径）。
    """

    def __init__(self, ch_client: Any | None = None) -> None:
        self._ch_client = ch_client

    def fetch_events(self, start: datetime.date, end: datetime.date) -> list["DabanBoardEvent"]:
        from zephyr.data.implementations.daban_board_event_deriver import collect_derived_events

        client = self._ch_client
        if client is None:
            from zephyr.infrastructure.database_service import get_db_service

            client = get_db_service().get_clickhouse_conn(role="reader")
        return collect_derived_events(start, end, client, sleep=lambda _s: None)


def fetch_float_cap_map(
    events: Sequence["DabanBoardEvent"],
    *,
    reader: Any | None = None,
) -> dict[tuple[str, str], float]:
    """流通市值真连接（只读）：stock_indicator.circ_mv（万元）×1e4 折元 → {(event_day_iso, symbol): 元}。

    挖矿 LUE-1 实证可产真字段（封单质量/资金因子分母）。reader 注入位（None=lazy
    ch_reader.query，TSV 返回；测试注 fake 零 DB）。查询异常 fail-open 空 map（对应字段
    default 留痕，非静默——与事件源同 fail-open 契约）。
    """
    if not events:
        return {}
    days = sorted({_iso_day(getattr(e, "trade_date")) for e in events})
    syms = sorted({str(getattr(e, "symbol")) for e in events})
    if not days or not syms:
        return {}
    dates_sql = ",".join(f"toDate('{d}')" for d in days)
    syms_sql = ",".join(f"'{s}'" for s in syms)
    sql = _SQL_CAP_BY_DAY_SYMBOLS.format(dates=dates_sql, symbols=syms_sql)
    try:
        if reader is None:
            from zephyr.data import ch_reader

            raw = ch_reader.query(sql)
        else:
            raw = reader(sql)
    except Exception as exc:  # noqa: BLE001 — fail-open 空（字段降 default）
        _logger.warning("float_market_cap 维度连接查询异常，降级 default（fail-open）: %s", exc)
        return {}
    out: dict[tuple[str, str], float] = {}
    for line in (raw or "").strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        mv = _tsv_val(parts[2])
        if mv is None:
            continue
        try:
            out[(_iso_day(parts[0]), str(parts[1]))] = float(mv) * _WAN_TO_YUAN
        except ValueError:
            continue
    return out


# ---------------------------------------------------------------------------
# 消费侧 PIT 读源（决策日 T 只读 trade_date < T 的最新事件日分区）
# ---------------------------------------------------------------------------


@runtime_checkable
class DabanEngineLoadSource(Protocol):
    """负载消费源协议（生产=ClickHouse PIT 读，测试=fake 注入）。"""

    def fetch_load(self, as_of_date: datetime.date) -> list[dict[str, Any]]: ...


class ClickHouseDabanEngineLoadSource:
    """daban_engine_load 表 PIT 读源——决策日 as_of 只回 <as_of 的最新事件日负载行。

    shift(1) 防未来函数：本表 trade_date=事件日（收盘后才知封板/close），决策日 T 取前一
    交易日分区。lazy import ch_reader，查询异常 fail-open 空（策略侧据此告警 skipped）。
    """

    def resolve_event_date(self, as_of_date: datetime.date) -> datetime.date | None:
        if not _is_date(as_of_date):
            raise ValueError(f"resolve_event_date: as_of_date 须为 date，实际 {type(as_of_date).__name__}")
        from zephyr.data import ch_reader

        sql = _SQL_LOAD_MAX_EVENT_DATE.format(as_of=as_of_date.isoformat())
        try:
            tsv = ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open（上层 fetch_load 空→策略告警）
            _logger.warning("daban_engine_load PIT 事件日解析异常（fail-open）: %s", exc)
            return None
        line = (tsv or "").strip().splitlines()
        if not line:
            return None
        token = line[0].strip()
        if not token or token in ("0000-00-00", "\\N"):
            return None
        try:
            resolved = datetime.date.fromisoformat(token[:10])
        except ValueError:
            return None
        # CH 对空 Date 列 max() 回 1970-01-01：判"无分区"而非"远古分区"
        if resolved < MIN_EVENT_DATE:
            return None
        return resolved

    def fetch_load(self, as_of_date: datetime.date) -> list[dict[str, Any]]:
        event_date = self.resolve_event_date(as_of_date)
        if event_date is None:
            return []
        return self._fetch_by_event_date(event_date)

    def _fetch_by_event_date(self, event_date: datetime.date) -> list[dict[str, Any]]:
        from zephyr.data import ch_reader

        sql = _SQL_LOAD_ROWS_BY_DATE.format(event_date=event_date.isoformat())
        try:
            tsv = ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open 空行
            _logger.warning("daban_engine_load 分区查询异常（fail-open）: %s", exc)
            return []
        rows: list[dict[str, Any]] = []
        for line in (tsv or "").strip().splitlines():
            parts = line.split("\t")
            if len(parts) != len(LOAD_INSERT_COLUMNS):
                continue
            row = _parse_load_tsv(parts)
            if row is None or not _valid_symbol(row["symbol"]):
                continue
            rows.append(row)
        return rows


def _parse_load_tsv(parts: Sequence[str]) -> dict[str, Any] | None:
    """TSV 字段 → 负载行 dict（\\N/空→None；数值列容错）。失败→None（调用方剔除）。"""
    values: list[Any] = list(parts)
    row: dict[str, Any] = {}
    int_cols = {"st_flag", "consec_limit", "open_board_count", "is_one_word", "sector_limit_up_count", "market_limit_up_count"}
    float_cols = {"seal_time_minutes", "seal_amount", "float_market_cap", "stock_change_pct", "close_price", "limit_up_price", "market_breadth_ratio", "market_change_pct"}
    for col, raw in zip(LOAD_INSERT_COLUMNS, values, strict=True):
        if col == "trade_date":
            row[col] = _iso_day(raw)
        elif col in ("symbol", "board", "first_touch_time", "derived_fields", "load_version", "data_source"):
            row[col] = None if raw in ("\\N", "") else str(raw)
        elif col in int_cols:
            row[col] = None if raw in ("\\N", "") else int(float(raw))
        elif col in float_cols:
            row[col] = None if raw in ("\\N", "") else float(raw)
    row["derived_fields"] = row.get("derived_fields") or "{}"
    return row


def _is_date(value: Any) -> bool:
    return isinstance(value, datetime.date) and not isinstance(value, datetime.datetime)


def _valid_symbol(symbol: Any) -> bool:
    return isinstance(symbol, str) and bool(_SYMBOL_RE.match(symbol))


# ---------------------------------------------------------------------------
# 批产编排（生产者入口——由 reconciler 链事件触发；本模块零时钟）
# ---------------------------------------------------------------------------


def run_daily_batch(
    event_day: datetime.date | str,
    *,
    event_source: DabanEventSource | None = None,
    market_context: Mapping[str, Mapping[str, float]] | None = None,
    cap_source: Any | None = fetch_float_cap_map,
) -> "FetchResult":
    """单日事件 → daban_engine_load 负载 FetchResult（不触发写、不调时钟）。

    Args:
        event_day: 打板事件日（=未来决策日的 T-1）。
        event_source: 事件源（None=ClickHouseDabanBoardEventSource；验证回填注 Derived 源）。
        market_context: 市场宽度/大盘涨幅注入位（None=相关字段 default）。
        cap_source: 流通市值真连接入 callable(events)->{(day,symbol):元}（默认
            fetch_float_cap_map；None=跳过→float_market_cap 字段 default，测试注 fake）。

    Returns:
        FetchResult（table/columns/rows/last_key=event_day）；空事件日 rows=[]（fail-visible warning）。
    """
    from zephyr.data.provider_base import FetchResult

    day = _coerce_date(event_day)
    source = event_source if event_source is not None else ClickHouseDabanBoardEventSource()
    events = source.fetch_events(day, day)
    if not events:
        _logger.warning("daban_load: 事件日 %s 零打板事件（表未派生或当日无事件）——负载空批，非静默", day.isoformat())
        return FetchResult(
            table=_TARGET_TABLE,
            columns=list(LOAD_INSERT_COLUMNS),
            rows=[],
            last_key=day.isoformat(),
            elapsed_sec=0.0,
            rows_fetched=0,
        )
    cap_map = cap_source(events) if cap_source is not None else None
    rows = events_to_load_rows(events, market_context=market_context, cap_map=cap_map)
    tuples = load_rows_to_tuples(rows)
    _logger.info("daban_load: 事件日 %s 产 %d 负载行（自 %d 事件）", day.isoformat(), len(tuples), len(events))
    return FetchResult(
        table=_TARGET_TABLE,
        columns=list(LOAD_INSERT_COLUMNS),
        rows=tuples,
        last_key=day.isoformat(),
        elapsed_sec=0.0,
        rows_fetched=len(tuples),
    )


def persist(result: "FetchResult", *, timeout: int = 600) -> bool:
    """负载 FetchResult → ClickHouse（ch_writer.write_result，列过滤/MATERIALIZED 排除内建）。

    生产落表入口；只读验证会话不调用。write_result 内部处理 HTTP/TCP + 本地落盘兜底。
    """
    from zephyr.data import ch_writer

    ok = ch_writer.write_result(result, timeout=timeout)
    if not ok:
        _logger.warning("daban_load: persist 失败（write_result 返回 False）table=%s rows=%d", result.table, len(result.rows))
    return ok


def _coerce_date(value: datetime.date | str) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


__all__: Final = [
    "CATEGORY_ID",
    "ClickHouseDabanBoardEventSource",
    "ClickHouseDabanEngineLoadSource",
    "DabanEngineLoadSource",
    "DabanEventSource",
    "DerivedDabanBoardEventSource",
    "LOAD_INSERT_COLUMNS",
    "LOAD_VERSION",
    "events_to_load_rows",
    "fetch_float_cap_map",
    "load_rows_to_tuples",
    "persist",
    "run_daily_batch",
    "seal_time_minutes_from_touch",
    "stock_change_pct",
]
