# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.ch_auction_derive
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.implementations.qmt_bridge_provider; scripts.backfill_auction_snapshot_history
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] INSERT-only 零 DELETE（目标表 ReplacingMergeTree 按键去重=天然幂等，快照表
#              (symbol,trade_date) 最后插入胜出=终态覆盖语义，与 miniqmt 原产一致）；
#              竞价窗口=[09:15:00, 09:26:00)（含 09:25:00 撮合打印行）；源表必须过滤
#              market_type IN ('stock','stock_bj')——tick_depth_5/tick_data 裸码跨市场复用
#              （'000001'=平安银行(stock) 与 上证指数(index) 同码不同市，实测 9/16 双族并存，
#              不滤市=指数行情灌进竞价表的事故）；量纲同源零换算（9/16 平银实证
#              tick_depth_5.stock volume/amount == auction_book 1,499 手/1,768,800 元逐位一致）；
#              book 六列复刻 miniqmt 竞价时段原产语义：open/high/low=0（9/16 原产实测即 0），
#              pre_close/upper_limit/lower_limit=昨收规则推导（pre_close=昨收 round 2 位交易所
#              口径；涨跌幅经 stk_limit 权威全表实证锁定：主板 10%（现行规则 ST 同幅）、
#              创业科创 20%、北交所 30%，9/16 对拍 000001 13.00/10.64 逐位一致）；五档空档 coalesce 0（对齐 dump 0 值惯例，
#              防 Nullable 源列 INSERT 失败）；data_source 透传源行（provenance 如实）；
#              pre_close 回看窗 60 天 per-symbol argMax（停牌/迟上市股兜底，红队 #6：
#              恰好前一交易日无行曾致 200 符号 pre_close=0）；None client 显式 RuntimeError
#              （get_client() 冷却期返 None，AttributeError 违反 ERROR_CONTRACT——红队 #5）
# [MODIFY-GUARD] schema-change
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源表空窗→返回 0 不报错；INSERT 失败抛 RuntimeError 由调用方降级；非法日期→ValueError
# [TESTS] tests/zephyr/data/test_ch_auction_derive.py
# [TTL] permanent
"""集合竞价表桥源派生（tick_depth_5/tick_data → auction_snapshot/auction_book）。

背景（迁移台账 §2.2-B 勘误+2026-09-17 挖矿文档
docs/_working/auction_bridge_switch_mining_2026_09_17.md）：auction 族原走
miniqmt get_full_tick 实时快照，2026-09-18 券商关停 miniQMT 后切桥派生——
桥 TICKDUMP3_v19 全市场 3 秒快照流（含五档）经 tick_subscriber 落
tick_depth_5，本模块把竞价窗口 [09:15,09:26) 的行 CH 内派生进两张竞价表，
消费端（scenario_planner/auction_hit_recorder）与表 schema 零改动。

派生语义（对 miniqmt 原产逐位对拍校准，9/16 平安银行实证）：
- auction_snapshot：每股窗口内 argMax(timestamp) 一行（终态覆盖）；
  auction_price/volume/amount=撮合终态（11.8/1499/1768800 逐位一致）
- auction_book：窗口内逐拍直插（键 symbol+trade_date+timestamp 天然去重）；
  last_price/volume/amount 直取，open/high/low=0（miniqmt 竞价时段原产即 0），
  pre_close/涨停/跌停=昨收规则推导（miniqmt 原产 pre_close=11.82/涨停 13.00/
  跌停 10.64，规则推导可复现）
- 量纲：两表 volume 单位=手，与 tick_depth_5.stock 同源零换算

INSERT-only（无 ALTER DELETE）：ReplacingMergeTree 按键去重，重复派生幂等；
auction_snapshot 键 (symbol,trade_date) 最后插入胜出=终态随竞价进程自然演进。
回补（历史日）只允许灌空日——调用方先用 day_has_auction_rows 检查，
禁止对已有 miniqmt 原产数据的日期重灌（防派生近似覆盖原产精确值）。
"""

from __future__ import annotations

import logging
import re

from zephyr.data.ch_writer import get_client
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 目标表（注册表真源派生，#ARCH-CH-024）
_TBL_SNAPSHOT = get_registry().table("market_auction_snapshot")
_TBL_BOOK = get_registry().table("market_auction_book")

# 源表：实时派生=tick_depth_5（五档全）；历史回补=tick_data（1 档，2026-06 起有竞价窗口）
_SRC_DEPTH = get_registry().table("market_tick_depth_5")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")

# 竞价窗口（含 09:25:00 撮合打印与撮合后数秒的终态确认行，9/16 实证 09:25:03 有打印）
_AUCTION_START = "09:15:00"
_AUCTION_END_EXCL = "09:26:00"

# 只取股票族——index/etf/lof/cb 与股票共用裸码空间，混入=灌表事故（见 INVARIANTS）
_STOCK_MARKET_TYPES = ("stock", "stock_bj")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# NO-BARE-SQL gate 豁免前缀（同 ch_tick_kline）
# ⚠ CH 别名遮蔽陷阱：SELECT 别名会被代入 WHERE——本查询 WHERE 过滤 market_type，
# 若常量列写 'A_share' AS market_type 则 WHERE 被改写为 'A_share' IN (...) 恒假
# （2026-09-17 回补 32 天全 0 行事故实证）。INSERT 列表按位置映射，常量列一律不取别名。
SQL_SNAPSHOT_SELECT = """
SELECT
    trade_date,
    max(timestamp) AS auction_time,
    symbol,
    argMax(price, timestamp) AS auction_price,
    argMax(volume, timestamp) AS auction_volume,
    argMax(amount, timestamp) AS auction_amount,
    'A_share',
    argMax(data_source, timestamp) AS data_source,
    toUInt8(1)
FROM {src}
WHERE trade_date = '{d}'
  AND market_type IN ('stock', 'stock_bj')
  AND timestamp >= '{d} {_AUCTION_START}' AND timestamp < '{d} {_AUCTION_END_EXCL}'
GROUP BY symbol, trade_date
"""

SQL_SNAPSHOT_INSERT = (
    "INSERT INTO {snap}\n"
    "    (trade_date, auction_time, symbol, auction_price, auction_volume,\n"
    "     auction_amount, market_type, data_source, quality_flag)\n"
    + SQL_SNAPSHOT_SELECT
)

# 五档 20 列共 coalesce 0（源 Nullable → 目标非 Nullable；空档 0 值=桥 dump 惯例）
_LEVEL_COALESCE = ",\n    ".join(
    f"coalesce(s.{col}, toDecimal64(0, 4)) AS {col}"
    if "price" in col
    else f"coalesce(s.{col}, toUInt64(0)) AS {col}"
    for col in [
        "bid_price1", "bid_price2", "bid_price3", "bid_price4", "bid_price5",
        "ask_price1", "ask_price2", "ask_price3", "ask_price4", "ask_price5",
        "bid_volume1", "bid_volume2", "bid_volume3", "bid_volume4", "bid_volume5",
        "ask_volume1", "ask_volume2", "ask_volume3", "ask_volume4", "ask_volume5",
    ]
)

# 昨收+涨跌停推导子查询（规则经 stk_limit 权威全表实证锁定，2026-09-15：
# 00/60 主板=10%（st_flag=1 亦 0.1——现行规则 ST 与主板同幅）、30/68=20%、92 等 BJ=30%）：
# - pre_close = 昨日 close 四舍五入到 2 位（交易所口径；kline_daily 存 4dp 有
#   101.9299 式伪影，不 round 则与交易所 pre_close 逐位失配——9/16 对拍实证），
#   且涨跌停 MUST 基于官方 2dp 昨收计算
# - 无 ST 特判（现行规则已并入主板幅；若交易所恢复 ST 差异幅，以 stk_limit 表为准另改）
_PRECLOSE_SUB = """
SELECT
    b.symbol,
    coalesce(b.close, toDecimal64(0, 4)) AS pre_close,
    coalesce(round(multiIf(
        startsWith(b.symbol, '30') OR startsWith(b.symbol, '68'), b.close * toDecimal64(1.2, 5),
        startsWith(b.symbol, '43') OR startsWith(b.symbol, '83') OR startsWith(b.symbol, '87') OR startsWith(b.symbol, '92'), b.close * toDecimal64(1.3, 5),
        b.close * toDecimal64(1.1, 5)
    ), 2), toDecimal64(0, 4)) AS upper_limit,
    coalesce(round(multiIf(
        startsWith(b.symbol, '30') OR startsWith(b.symbol, '68'), b.close * toDecimal64(0.8, 5),
        startsWith(b.symbol, '43') OR startsWith(b.symbol, '83') OR startsWith(b.symbol, '87') OR startsWith(b.symbol, '92'), b.close * toDecimal64(0.7, 5),
        b.close * toDecimal64(0.9, 5)
    ), 2), toDecimal64(0, 4)) AS lower_limit
FROM (
    SELECT symbol, round(argMax(close, trade_date), 2) AS close
    FROM {kd}
    WHERE trade_date < '{d}'
      AND trade_date >= (
        SELECT max(trade_date) FROM {kd} WHERE trade_date < '{d}'
      ) - INTERVAL 60 DAY
    GROUP BY symbol
) b
"""

SQL_BOOK_SELECT = (
    "SELECT\n"
    "    s.trade_date,\n"
    "    s.timestamp,\n"
    "    s.symbol,\n"
    "    s.price AS last_price,\n"
    "    s.volume,\n"
    "    s.amount,\n"
    "    toDecimal64(0, 4) AS open,\n"
    "    toDecimal64(0, 4) AS high,\n"
    "    toDecimal64(0, 4) AS low,\n"
    "    coalesce(k.pre_close, toDecimal64(0, 4)) AS pre_close,\n"
    "    coalesce(k.upper_limit, toDecimal64(0, 4)) AS upper_limit,\n"
    "    coalesce(k.lower_limit, toDecimal64(0, 4)) AS lower_limit,\n"
    "    " + _LEVEL_COALESCE + ",\n"
    "    s.data_source\n"
    "FROM {src} s\n"
    "LEFT JOIN ("
    + _PRECLOSE_SUB
    + ") k ON k.symbol = s.symbol\n"
    "WHERE s.trade_date = '{d}'\n"
    "  AND s.market_type IN ('stock', 'stock_bj')\n"
    "  AND s.timestamp >= '{d} " + _AUCTION_START + "' AND s.timestamp < '{d} " + _AUCTION_END_EXCL + "'\n"
)

SQL_BOOK_INSERT = (
    "INSERT INTO {book}\n"
    "    (trade_date, timestamp, symbol, last_price, volume, amount,\n"
    "     open, high, low, pre_close, upper_limit, lower_limit,\n"
    "     bid_price1, bid_price2, bid_price3, bid_price4, bid_price5,\n"
    "     ask_price1, ask_price2, ask_price3, ask_price4, ask_price5,\n"
    "     bid_volume1, bid_volume2, bid_volume3, bid_volume4, bid_volume5,\n"
    "     ask_volume1, ask_volume2, ask_volume3, ask_volume4, ask_volume5,\n"
    "     data_source)\n"
    + SQL_BOOK_SELECT
)


# 行数核对（count 走常量，NO-BARE-SQL 同口径）
SQL_COUNT_DAY = "SELECT count() FROM {table} WHERE trade_date = '{d}'"


def _validate_date(d: str) -> str:
    if not _DATE_RE.match(d or ""):
        raise ValueError(f"非法日期（需 YYYY-MM-DD）: {d!r}")
    return d


def _snapshot_select_sql(d: str, src: str | None = None) -> str:
    """竞价快照终态 SELECT（独立导出供 E2E 对拍零写入验证；src 可换 tick_data
    供 2026-06~08 空窗日回补——1 档源亦有 market_type 防指数混线）。"""
    return SQL_SNAPSHOT_SELECT.format(
        src=src or _SRC_DEPTH,
        d=_validate_date(d),
        _AUCTION_START=_AUCTION_START,
        _AUCTION_END_EXCL=_AUCTION_END_EXCL,
    )


def _book_select_sql(d: str) -> str:
    """竞价盘口逐拍 SELECT（独立导出供 E2E 对拍零写入验证）。"""
    return SQL_BOOK_SELECT.format(
        src=_SRC_DEPTH,
        kd=_TBL_KLINE_DAILY,
        d=_validate_date(d),
        _AUCTION_START=_AUCTION_START,
        _AUCTION_END_EXCL=_AUCTION_END_EXCL,
    )


def derive_auction_snapshot(trade_date: str, client=None, src_table: str | None = None) -> int:
    """tick_depth_5 竞价窗口 → auction_snapshot 终态（每股一行，INSERT-only 幂等）。

    Args:
        trade_date: 派生日（YYYY-MM-DD）。
        client: CH client（默认 ch_writer writer）。
        src_table: 源表覆盖——历史回补 2026-06~08 空窗日传 tick_data（1 档，
            该源亦有 market_type 防指数混线）；实时派生默认 tick_depth_5。

    Returns:
        派生后该日快照表行数。源窗口无数据返回 0（幂等正常态，不报错）。
    Raises:
        RuntimeError: INSERT 失败（调用方降级为 FetchResult(error=...)）。
    """
    d = _validate_date(trade_date)
    if client is None:
        client = get_client()
    if client is None:
        raise RuntimeError("ch_writer get_client() 返回 None（连接冷却期），竞价派生无法执行")
    try:
        client.execute(
            SQL_SNAPSHOT_INSERT.format(
                snap=_TBL_SNAPSHOT,
                src=src_table or _SRC_DEPTH,
                d=d,
                _AUCTION_START=_AUCTION_START,
                _AUCTION_END_EXCL=_AUCTION_END_EXCL,
            )
        )
    except Exception as e:  # noqa: BLE001 — 统一转 RuntimeError 语义
        raise RuntimeError(f"{_TBL_SNAPSHOT} 竞价快照派生失败 [{d}]: {e}") from e
    n = client.execute(
        SQL_COUNT_DAY.format(table=_TBL_SNAPSHOT, d=d)
    )[0][0]
    log.info("derive_auction_snapshot [%s]: 表内 %d 行", d, n)
    return int(n)


def derive_auction_book(trade_date: str, client=None) -> int:
    """tick_depth_5 竞价窗口 → auction_book 逐拍五档（含 6 列规则推导，INSERT-only 幂等）。

    Returns:
        派生后该日盘口表行数。源窗口无数据返回 0。
    Raises:
        RuntimeError: INSERT 失败。
    """
    d = _validate_date(trade_date)
    if client is None:
        client = get_client()
    if client is None:
        raise RuntimeError("ch_writer get_client() 返回 None（连接冷却期），竞价派生无法执行")
    try:
        client.execute(
            SQL_BOOK_INSERT.format(
                book=_TBL_BOOK,
                src=_SRC_DEPTH,
                kd=_TBL_KLINE_DAILY,
                d=d,
                _AUCTION_START=_AUCTION_START,
                _AUCTION_END_EXCL=_AUCTION_END_EXCL,
            )
        )
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"{_TBL_BOOK} 竞价盘口派生失败 [{d}]: {e}") from e
    n = client.execute(
        SQL_COUNT_DAY.format(table=_TBL_BOOK, d=d)
    )[0][0]
    log.info("derive_auction_book [%s]: 表内 %d 行", d, n)
    return int(n)


def day_has_auction_rows(client, table: str, trade_date: str) -> bool:
    """目标表该日是否已有数据（回补防重灌闸：已有行=跳过，禁覆盖原产）。"""
    n = client.execute(
        SQL_COUNT_DAY.format(table=table, d=_validate_date(trade_date))
    )[0][0]
    return int(n) > 0
