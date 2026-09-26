# [BLUEPRINT] MOD-WO004-HFQ-RECALC | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-004
# [MODULE] scripts.governance.meta_question.wo004.recalc_hfq
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service (reader 探针/对拍复核); zephyr.data.ch_writer (writer 通道 get_client); zephyr.data.table_registry (表名品类真源 #ARCH-CH-024)
# [CONSUMERS] scripts/governance/meta_question/wo004/verify_hfq.py（复用本件真源表达式，单一口径定义）； 人工换名/回滚（对拍全绿 + Owner 门位后）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 可逆性三步铁律（宪法 §1 RULE-DATA-OPS）：绝不原地 DELETE/ALTER 覆写生产表—— ①只建同构新表 kline_daily_hfq_recalc ②对拍四项全绿才 --swap 原子换名 ③旧表改名 legacy 留存（换名是唯一动作，回滚=反向 RENAME，零数据丢失）； 口径唯一真源 = kline_daily(raw) × adj_factor(data_source='bdpan')，禁调容差蒙混； 分片幂等：按自然月 ALTER ... DROP PARTITION + INSERT 重灌，中断可续跑，无双写残留； 逐行纯函数：产出每一行只依赖 (raw 行, 因子行)，无窗口/链式依赖 ⇒ 抽检器可对任意点 独立复算而不必重建全链（这是本单可长期例行化的结构前提）； 量纲契约（现表 100% 实证，非推测）：volume=intDiv(raw.volume,100)、amount/turnover 透传、 OHLC×因子；amplitude/pct_change/change 维持 DEFAULT 0（链式衍生列不在口径裁定内， 现表 99.95% 亦为 0，见交付件决策 D5）； 断供外推有界：仅在 bdpan 末值锚点 d0 ≥ dr 事件流首日（2026-07-01）且行日 > 2026-07-03 时以 dr 累计外推，杜绝跨无事件流区间的外推（防注入新幻影）； fail-visible：任一分片异常即抛出终止并保留现场（不 swap）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 建表/分片 INSERT 失败→抛出并终止（已灌分片保留，重跑先 DROP PARTITION 再灌）； --swap 前置=读对拍报告 JSON 的 gates 四项全真，缺报告/未全绿一律拒绝换名并退出码 2。
# [TESTS] 无 pytest（一次性运维管线，同族 scripts/ch/backfill_* 先例）； 验收=verify_hfq.py 四项对拍数字（本单核心工作量在对拍，非灌数）。
# [A_module] module_id=MOD-WO004-HFQ-RECALC | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""recalc_hfq — kline_daily_hfq 全表按 raw×adj_factor 重算（WO-004，PQ-0012/0131 复权链治本）。

缺口（本单实测坐实）：现表系外部后复权报价流直落（data_source 默认值 'bdpan_hfq' 掩盖
miniqmt back 混写），与 raw×adj_factor 既不同量级（600519 2024-01 隐含因子 5.577 vs bdpan 7.8576，
低 29%）又不同形状（2021 抽 90 只中 79 只 hfq/(raw×factor) 内部散布 >0.2%，最大 271%）
⇒ 抽检验算违例率 45.4%（PQ-0012/0131 fail·infra）。

重建口径：hfq = raw × 后复权累计因子（上市日=1 起算，按日生效，PIT 安全——后复权不追溯改写）。
  * 主链 c1_market.adj_factor data_source='bdpan'（1990-12-19~2026-07-03，5,860 只，
    与 kline_daily A 股键 2019+ 重合率 99.95~100%，因子无 ≤0/无极端值）；
  * 2026-07-04 起 bdpan 停更（月匹配率 202606=100% → 202607=13.0% → 202608=0%），
    以本票末值 × miniQMT 除权除息系数 dr 累计外推（dr 语义实证：1,039 事件日
    prev_close/(close×dr) 中位数 = 1.0000007 ⇒ dr 就是累计因子的乘性步长，与 bdpan 同口径）；
  * kline_daily 内嵌 adj_factor 列全表恒为 1（10,102,587/10,102,587 行，死列）⇒ 禁为乘子。

用法（顺序即验收顺序，禁跳步）：
    python scripts/governance/meta_question/wo004/recalc_hfq.py --create
    python scripts/governance/meta_question/wo004/recalc_hfq.py --run [--resume] [--start --end]
    python scripts/governance/meta_question/wo004/recalc_hfq.py --status
    python scripts/governance/meta_question/wo004/verify_hfq.py --out .../verify_latest.json
    python scripts/governance/meta_question/wo004/recalc_hfq.py --swap --yes
    python scripts/governance/meta_question/wo004/recalc_hfq.py --rollback --yes
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from typing import Final

if __package__ in (None, ""):  # 直连脚本运行（未作为包 import）时的 sys.path 兜底
    for _p in ("src", "."):
        if _p not in sys.path:
            sys.path.insert(0, _p)

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

# ------------------------------------------------------------ 表名常量（唯一真源=品类册，抽检器同引）
# 旁挂表 *_recalc / *_legacy_20260924 是本管线自建的影子表、不在品类册内，故一律由已注册
# 基表派生（#ARCH-CH-024：禁把自建表名塞进 TableRegistry，品类真源唯一 ⇒ 衍生名可证）。
RAW_TABLE: Final = get_registry().table("market_kline_daily")
HFQ_TABLE: Final = get_registry().table("market_kline_daily_hfq")
RECALC_TABLE: Final = f"{HFQ_TABLE}_recalc"
LEGACY_TABLE: Final = f"{HFQ_TABLE}_legacy_20260924"
FACTOR_TABLE: Final = get_registry().table("market_adj_factor")

# ------------------------------------------------------------ 因子口径常量（实测钉死，勿改）
FACTOR_MAIN: Final = "bdpan"  # 主链：按日累计后复权因子（上市日=1 起算）
FACTOR_EVENT: Final = "miniqmt"  # 外推腿：除权除息系数 dr（仅主链断供后启用）
CUTOFF: Final = dt.date(2026, 7, 3)  # bdpan 主链最后可用日（实测）
DR_STREAM_START: Final = dt.date(2026, 7, 1)  # miniqmt dr 事件流首日（实测，外推下界）
PQ_CUTOFF: Final = dt.date(2025, 9, 9)  # 283 问闭卷切点（复考窗上限）
DATA_SOURCE_MARK: Final = "recalc_raw_x_adjfactor"  # 血统自证：不复用 'bdpan_hfq' 假标记
FIRST_MONTH: Final = dt.date(1990, 12, 1)  # kline_daily 最早数据月（实测 1990-12-19）

INSERT_COLS: Final = (
    "trade_date, symbol, open, close, high, low, volume, amount, amplitude, pct_change, change, turnover, data_source"
)

_SETTINGS: Final = {"max_execution_time": 0, "connect_timeout": 10, "output_format_write_statistics": 0}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。全部语句以 {} 占位承载表名/口径值与 PIT 日期窗，
# 由调用点 .format() 注入——常量内禁落任何日期字面量；渲染结果与提取前的逐字函数体等值。
_SQL_RAW = (
    "SELECT trade_date, symbol, {ohlc}, "
    "argMax(volume, ingest_ts) AS v, "
    "argMax(amount, ingest_ts) AS amt, "
    "argMax(turnover, ingest_ts) AS tr "
    "FROM {raw_table} "
    "WHERE market_type = 'A_share' AND trade_date BETWEEN '{lo}' AND '{hi}' "
    "AND close > 0 AND open > 0 AND high > 0 AND low > 0 AND high >= low "
    "AND isFinite(toFloat64(close)) "
    "GROUP BY trade_date, symbol"
)
_SQL_FACTOR_MAIN = (
    "SELECT symbol, trade_date, "
    "CAST(argMax(adj_factor, ingest_ts) AS Decimal(18, 8)) AS f "
    "FROM {factor_table} "
    "WHERE data_source = '{main}' AND trade_date BETWEEN '{lo}' AND '{hi}' "
    "AND adj_factor > 0 AND isFinite(toFloat64(adj_factor)) "
    "GROUP BY symbol, trade_date"
)
_SQL_FACTOR_ANCHOR = (
    "SELECT symbol, d0, f0 FROM ("
    "  SELECT symbol, max(trade_date) AS d0, "
    "    CAST(argMax(adj_factor, trade_date) AS Decimal(18, 8)) AS f0 "
    "  FROM {factor_table} WHERE data_source = '{main}' AND adj_factor > 0 "
    "  AND symbol IN (SELECT DISTINCT symbol FROM {raw_table} "
    "                 WHERE trade_date BETWEEN '{lo}' AND '{hi}') "
    "  GROUP BY symbol HAVING d0 >= toDate('{dr_start}')"
    ") "
    "UNION ALL "
    "SELECT n.symbol AS symbol, n.d0 AS d0, CAST(1, 'Decimal(18, 8)') AS f0 FROM ("
    "  SELECT symbol, min(trade_date) AS fd, subtractDays(min(trade_date), 1) AS d0 "
    "  FROM {raw_table} WHERE market_type = 'A_share' "
    "  AND trade_date BETWEEN '{lookback}' AND '{hi}' GROUP BY symbol "
    "  HAVING fd > toDate('{cutoff}')"
    ") AS n LEFT ANTI JOIN ("
    "  SELECT symbol FROM {factor_table} WHERE data_source = '{main}' GROUP BY symbol"
    ") AS o ON n.symbol = o.symbol"
)
_SQL_FACTOR_EVENTS = (
    "SELECT symbol, groupArray(tuple(trade_date, log(toFloat64(adj_factor)))) AS evs "
    "FROM {factor_table} WHERE data_source = '{event}' AND adj_factor > 0 "
    "GROUP BY symbol"
)
_SQL_FACTOR_SPLICE = (
    "SELECT k.symbol AS symbol, k.trade_date AS trade_date, "
    "toDecimal128(an.f0 * exp(arraySum(arrayMap(x -> x.2, "
    "arrayFilter(x -> x.1 > an.d0 AND x.1 <= k.trade_date, ev.evs)))), 12) AS f "
    "FROM ({raw}) AS k "
    "INNER JOIN ({anchor}) AS an ON k.symbol = an.symbol "
    "LEFT JOIN ({events}) AS ev ON k.symbol = ev.symbol "
    "WHERE k.trade_date > an.d0 AND k.trade_date > toDate('{cutoff}')"
)
_SQL_SHARD_LEG_MAIN = (
    "SELECT k.trade_date AS trade_date, k.symbol AS symbol, k.o AS o, k.c AS c, k.h AS h, "
    "k.l AS l, k.v AS v, k.amt AS amt, k.tr AS tr, f.f AS f "
    "FROM ({raw}) AS k "
    "INNER JOIN ({fmain}) AS f "
    "ON k.symbol = f.symbol AND k.trade_date = f.trade_date"
)
_SQL_SHARD_LEG_SPLICE = (
    "SELECT k.trade_date AS trade_date, k.symbol AS symbol, k.o AS o, k.c AS c, k.h AS h, "
    "k.l AS l, k.v AS v, k.amt AS amt, k.tr AS tr, sp.f AS f "
    "FROM ({raw}) AS k "
    "INNER JOIN ({spliced}) AS sp "
    "ON k.symbol = sp.symbol AND k.trade_date = sp.trade_date "
    "LEFT ANTI JOIN ({fmain}) AS m "
    "ON k.symbol = m.symbol AND k.trade_date = m.trade_date"
)
_SQL_SHARD_INSERT = (
    "INSERT INTO {recalc} ({cols}) "
    "SELECT trade_date, symbol, "
    "{o} AS open, {c} AS close, "
    "{h} AS high, {l} AS low, "
    "toUInt64(intDiv(v, 100)) AS volume, amt AS amount, "
    "toDecimal64(0, 4) AS amplitude, toDecimal64(0, 4) AS pct_change, "
    "toDecimal64(0, 4) AS change, tr AS turnover, "
    "'{mark}' AS data_source "
    "FROM ({src})"
)
_SQL_DROP_TABLE = "DROP TABLE {recalc}"
# ------------------------------------------------------------ ①/③ 落地腿：把重算结果提升进生产表
# 语义=幂等补齐 + 逐出非裁定口径：
#   fill  = 只补"该键在生产里没有裁定口径行"的键（同键同口径已存在则不重复灌，避免自叠行）；
#   evict = 把窗内 lineage_version 低于裁定口径的行（厂商 back 口径/陈旧快照）整批逐出。
# 配合 ③ 的 ReplacingMergeTree(lineage_version) ⇒ 即便逐出前被读到，FINAL 也已由版本列判裁定口径赢。
CANON_LINEAGE_VERSION: Final = 100
_SQL_PROMOTE_FILL = (
    "INSERT INTO {hfq} (" + INSERT_COLS + ", lineage_version) "
    "SELECT s.trade_date, s.symbol, s.open, s.close, s.high, s.low, s.volume, s.amount, "
    "s.amplitude, s.pct_change, s.change, s.turnover, s.data_source, {ver} "
    "FROM (SELECT * FROM {recalc} WHERE trade_date BETWEEN '{lo}' AND '{hi}') AS s "
    "LEFT ANTI JOIN (SELECT symbol, trade_date FROM {hfq} "
    "WHERE lineage_version >= {ver} AND trade_date BETWEEN '{lo}' AND '{hi}') AS p "
    "ON p.symbol = s.symbol AND p.trade_date = s.trade_date"
)
_SQL_PROMOTE_EVICT = "ALTER TABLE {hfq} DELETE WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND lineage_version < {ver}"
_SQL_PROMOTE_PENDING = (
    "SELECT count() FROM (SELECT s.symbol AS sym, s.trade_date AS dt FROM "
    "(SELECT symbol, trade_date FROM {recalc} WHERE trade_date BETWEEN '{lo}' AND '{hi}') AS s "
    "LEFT ANTI JOIN (SELECT symbol, trade_date FROM {hfq} WHERE lineage_version >= {ver} "
    "AND trade_date BETWEEN '{lo}' AND '{hi}') AS p ON p.symbol = s.symbol AND p.trade_date = s.trade_date)"
)
_SQL_PROMOTE_STALE = "SELECT count() FROM {hfq} WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND lineage_version < {ver}"
_SQL_PROMOTE_WINDOW = (
    "SELECT lineage_version, data_source, count() FROM {hfq} "
    "WHERE trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY 1, 2 ORDER BY 3 DESC"
)
_SQL_PROMOTE_DUPKEYS = (
    "SELECT count() FROM (SELECT symbol, trade_date FROM {hfq} "
    "WHERE trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol, trade_date HAVING count() > 1)"
)
_SQL_HAS_LINEAGE_COL = (
    "SELECT count() FROM system.columns WHERE database='c1_market' AND table='{tbl}' AND name='lineage_version'"
)
_SQL_CREATE_LIKE = (
    "CREATE TABLE {recalc} AS {hfq} "
    "ENGINE = ReplacingMergeTree "
    "PARTITION BY toYYYYMM(trade_date) "
    "ORDER BY (symbol, trade_date)"
)
_SQL_TABLE_KEYS = (
    "SELECT engine, sorting_key, partition_key FROM system.tables WHERE database='c1_market' AND name='{name}'"
)
_SQL_TABLE_COLUMNS = (
    "SELECT name,type,default_kind,default_expression FROM system.columns "
    "WHERE database='c1_market' AND table='{name}' ORDER BY position"
)
_SQL_TABLE_EXISTS = "SELECT count() FROM system.tables WHERE database='{db}' AND name='{tbl}'"
_SQL_COUNT_IN = "SELECT count() FROM {table} WHERE trade_date BETWEEN '{lo}' AND '{hi}'"
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"
_SQL_DONE_MONTHS = "SELECT DISTINCT toYYYYMM(trade_date) FROM {table}"
_SQL_PART_ACTIVE = (
    "SELECT count() FROM system.parts WHERE database='c1_market' "
    "AND table='{name}' AND partition_id='{ym}' AND active=1"
)
_SQL_ALTER_DROP_PARTITION = "ALTER TABLE {recalc} DROP PARTITION {ym}"
_SQL_STATUS_AGG = (
    "SELECT count(), uniqExact(symbol), min(trade_date), max(trade_date), "
    "countDistinct(toYYYYMM(trade_date)) FROM {table}"
)
_SQL_UNIQUE_KEYS = "SELECT uniqExact((symbol,trade_date)) FROM {table}"
_SQL_LINEAGE_DIST = "SELECT data_source, count() FROM {table} GROUP BY data_source ORDER BY 2 DESC"
_SQL_SWAP_RENAME = "RENAME TABLE {hfq} TO {legacy}, {recalc} TO {hfq}"
_SQL_ROLLBACK_RENAME = "RENAME TABLE {hfq} TO {recalc}, {legacy} TO {hfq}"


def d(x: dt.date) -> str:
    return x.strftime("%Y-%m-%d")


# ------------------------------------------------------------ 量纲/精度契约（实测钉死）
# ① 全程 Decimal 域相乘，禁经 Float64：CH 的 Float→Decimal 与 Decimal 降 scale 转换均"向零截断"，
#    走 float 会使 ~32% 行比精确乘积低整整 1 个末位单位（1e-4）——本单实测复现并纠正；
#    末位统一由 round(Decimal,4) 做四舍五入（CH 该函数对 Decimal 为 half-up），CAST 时值已是 4 位
#    小数故不再截断。抽检器据此可用 decimal.ROUND_HALF_UP 独立复算逐位回核。
# ② volume = intDiv(raw.volume,100)：现表 2026-01..09 逐月 100% 满足 volume×100 = raw.volume
#    （109,285/109,285 等），amount/turnover 与复权无关故透传（现表 amount 与 raw 逐位相等）。
# ③ amplitude/pct_change/change 维持 DEFAULT 0（链式衍生列不在本单口径裁定内，现表 99.95% 亦为 0）。
_RAW_OHLC: Final = (
    "argMax(open, ingest_ts) AS o, argMax(close, ingest_ts) AS c, "
    "argMax(high, ingest_ts) AS h, argMax(low, ingest_ts) AS l"
)


def _adj4(expr: str) -> str:
    """Decimal 乘积 → 末位 4 位四舍五入（half-up）→ Decimal(18,4)。"""
    return f"CAST(round({expr}, 4) AS Decimal(18, 4))"


# ------------------------------------------------------------ 真源表达式：raw 腿（去重）
def sql_raw(lo: dt.date, hi: dt.date) -> str:
    """原始 K 线去重为唯一 (symbol, trade_date)，价格保持原生 Decimal 不参与 float。

    kline_daily 是 ReplacingMergeTree 且无版本列（实测 97 个重复键，且重复行 close 同值），
    故用 GROUP BY + argMax(ingest_ts) 显式定值，不依赖 part 合并进度（FINAL 语义等价但可预测）。
    """
    return _SQL_RAW.format(ohlc=_RAW_OHLC, raw_table=RAW_TABLE, lo=d(lo), hi=d(hi))


# ------------------------------------------------------------ 真源表达式：因子主链
def sql_factor_main(lo: dt.date, hi: dt.date) -> str:
    return _SQL_FACTOR_MAIN.format(factor_table=FACTOR_TABLE, main=FACTOR_MAIN, lo=d(lo), hi=d(hi))


# ------------------------------------------------------------ 真源表达式：外推腿
def sql_factor_anchor(lo: dt.date, hi: dt.date) -> str:
    """外推起点锚 (symbol, d0=末有效日, f0=该日因子)，严格两支，杜绝跨"无事件流区间"外推：

    ① 主链在档：bdpan 末值日 d0 ≥ dr 事件流首日（若 d0 更早，则 (d0, t] 中存在既无主链
       又无事件流的区间，可能漏除权事件 ⇒ 宁缺不造，该类行只登记不合成）；
    ② 断供后新上市：kline_daily 首根 K 线晚于 CUTOFF 且主链完全无档 ⇒ 后复权定义即 f=1 起算，
       d0=上市日-1（其全部事件都落在 dr 流内）。
    """
    lookback = lo - dt.timedelta(days=200)
    return _SQL_FACTOR_ANCHOR.format(
        factor_table=FACTOR_TABLE,
        raw_table=RAW_TABLE,
        main=FACTOR_MAIN,
        lo=d(lo),
        hi=d(hi),
        dr_start=d(DR_STREAM_START),
        lookback=d(lookback),
        cutoff=d(CUTOFF),
    )


def sql_factor_events() -> str:
    """每票 dr 事件序列 [(date, ln(dr))]（仅锚点日之后的事件参与，防与主链重复计数）。"""
    return _SQL_FACTOR_EVENTS.format(factor_table=FACTOR_TABLE, event=FACTOR_EVENT)


def sql_factor_splice(lo: dt.date, hi: dt.date) -> str:
    """断供段因子 = f0 × exp(Σ ln(dr))，dr ∈ (d0, trade_date]。与主链严格不相交（trade_date > d0）。

    exp/log 只能在 float 域做（dr 每票 ≤ 数个，相对误差 ~1e-15），故落到 Decimal(38,12)
    （非 18,8：12 位小数的截断误差 ≤1e-12，经 raw×f 放大后仍 ≪ 末位 1e-4 的四舍五入界，
    实测消除外推段全部 1 末位单位偏差）再进 Decimal 乘法链。
    """
    return _SQL_FACTOR_SPLICE.format(
        raw=sql_raw(lo, hi), anchor=sql_factor_anchor(lo, hi), events=sql_factor_events(), cutoff=d(CUTOFF)
    )


# ------------------------------------------------------------ 分片 SQL
def shard_sql(month: dt.date) -> str:
    """单月灌数 SQL：主链段 ∪ 外推段（两段按 (symbol,trade_date) 严格互斥）。"""
    lo, hi = month_bounds(month)
    raw, fmain = sql_raw(lo, hi), sql_factor_main(lo, hi)
    leg_main = _SQL_SHARD_LEG_MAIN.format(raw=raw, fmain=fmain)
    if hi <= CUTOFF:
        src = leg_main
    else:
        leg_sp = _SQL_SHARD_LEG_SPLICE.format(raw=raw, fmain=fmain, spliced=sql_factor_splice(lo, hi))
        src = f"{leg_main} UNION ALL {leg_sp}"
    return _SQL_SHARD_INSERT.format(
        recalc=RECALC_TABLE,
        cols=INSERT_COLS,
        o=_adj4("o * f"),
        c=_adj4("c * f"),
        h=_adj4("h * f"),
        l=_adj4("l * f"),
        mark=DATA_SOURCE_MARK,
        src=src,
    )


# ------------------------------------------------------------ 分片调度工具
def month_bounds(month: dt.date) -> tuple[dt.date, dt.date]:
    lo = dt.date(month.year, month.month, 1)
    nxt = dt.date(lo.year + 1, 1, 1) if lo.month == 12 else dt.date(lo.year, lo.month + 1, 1)
    return lo, nxt - dt.timedelta(days=1)


def month_list(a: dt.date, b: dt.date) -> list[dt.date]:
    out: list[dt.date] = []
    cur = dt.date(a.year, a.month, 1)
    while cur <= b:
        out.append(cur)
        cur = dt.date(cur.year + 1, 1, 1) if cur.month == 12 else dt.date(cur.year, cur.month + 1, 1)
    return out


# ------------------------------------------------------------ 连接（模块级缓存，避免逐片重建）
_W: object | None = None
_R: object | None = None


def wclient():
    global _W
    if _W is None:
        c = ch_writer.get_client()
        if c is None:
            raise RuntimeError("CH writer TCP 不可用（ch_writer.get_client() -> None）——拒绝空跑")
        _W = c
    return _W


def reader():
    global _R
    if _R is None:
        from zephyr.infrastructure.database_service import DatabaseService

        _R = DatabaseService().get_clickhouse_conn(role="reader")
    return _R


def scalar(sql: str, default=None):
    rows = reader().execute(sql)
    if not rows or rows[0][0] is None:
        return default
    v = rows[0][0]
    return v


def table_exists(name: str) -> bool:
    db, tbl = name.split(".")
    return bool(scalar(_SQL_TABLE_EXISTS.format(db=db, tbl=tbl), 0))


def count_in(month: dt.date, table: str) -> int:
    lo, hi = month_bounds(month)
    return int(scalar(_SQL_COUNT_IN.format(table=table, lo=d(lo), hi=d(hi)), 0))


# ------------------------------------------------------------ 子命令
def cmd_create(args: argparse.Namespace) -> int:
    c = wclient()
    if table_exists(RECALC_TABLE):
        if not args.force:
            print(f"[skip] {RECALC_TABLE} 已存在（--force 才允许 DROP 重建；现表永不受本件影响）")
        else:
            print(f"[drop] {RECALC_TABLE}")
            c.execute(_SQL_DROP_TABLE.format(recalc=RECALC_TABLE))
            _create_like(c)
    else:
        _create_like(c)
    return 0


def _create_like(c) -> None:
    ddl = _SQL_CREATE_LIKE.format(recalc=RECALC_TABLE, hfq=HFQ_TABLE)
    print(f"[ddl] {ddl}")
    c.execute(ddl)
    short = RECALC_TABLE.split(".")[1]
    got = reader().execute(_SQL_TABLE_KEYS.format(name=short))
    src = reader().execute(_SQL_TABLE_KEYS.format(name=HFQ_TABLE.split(".")[1]))
    print(f"[check] recalc={got[0]}\n[check] src   ={src[0]}")
    cols_r = reader().execute(_SQL_TABLE_COLUMNS.format(name=short))
    cols_s = reader().execute(_SQL_TABLE_COLUMNS.format(name=HFQ_TABLE.split(".")[1]))
    if got[0] != src[0] or cols_r != cols_s:
        raise RuntimeError(f"重算表与现表不同构：engine/keys={got[0] != src[0]} cols={len(cols_r)}/{len(cols_s)}")
    print(f"[ok] 同构确认：{len(cols_r)} 列全等（含 exchange/symbol_canonical MATERIALIZED 派生列）")


def cmd_run(args: argparse.Namespace) -> int:
    c = wclient()
    if not table_exists(RECALC_TABLE):
        print("[abort] 重算表不存在——先 --create")
        return 2
    src_max = scalar(_SQL_MAX_TRADE_DATE.format(table=RAW_TABLE))
    lo = args.start or FIRST_MONTH
    hi = args.end or src_max
    months = month_list(lo, hi)
    done = {int(x[0]) for x in reader().execute(_SQL_DONE_MONTHS.format(table=RECALC_TABLE))}
    todo = [m for m in months if int(m.strftime("%Y%m")) not in done] if args.resume else months
    print(
        f"[run] 窗口 {d(lo)}..{d(hi)}（raw max={d(src_max)}）分片 {len(months)} 自然月，"
        f"已存在分片 {len(done)}，本次执行 {len(todo)}"
    )
    t0 = dt.datetime.now()
    total = 0
    for i, m in enumerate(todo, 1):
        ym = int(m.strftime("%Y%m"))
        if int(scalar(_SQL_PART_ACTIVE.format(name=RECALC_TABLE.split(".")[1], ym=ym), 0)):
            c.execute(_SQL_ALTER_DROP_PARTITION.format(recalc=RECALC_TABLE, ym=ym))
        sql = shard_sql(m)
        c.execute(sql, settings=_SETTINGS)
        n = count_in(m, RECALC_TABLE)
        total += n
        if i % args.echo_every == 0 or i == len(todo):
            el = (dt.datetime.now() - t0).total_seconds()
            print(f"  [{i}/{len(todo)}] {ym} rows={n} 累计={total} 用时={el:.0f}s")
        if args.limit_months and i >= args.limit_months:
            print(f"  [stop] --limit-months={args.limit_months} 试跑截止")
            break
    print(f"[done] 覆盖 {total} 行 / {len(todo)} 片（幂等可续跑：--resume 跳过已有分片）")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if not table_exists(RECALC_TABLE):
        print(f"[status] {RECALC_TABLE} 不存在")
        return 1
    q = _SQL_STATUS_AGG
    print("recalc (rows, syms, min_d, max_d, months):", tuple(reader().execute(q.format(table=RECALC_TABLE))[0]))
    print("legacy (rows, syms, min_d, max_d, months):", tuple(reader().execute(q.format(table=HFQ_TABLE))[0]))
    print("recalc 去重后唯一键:", scalar(_SQL_UNIQUE_KEYS.format(table=RECALC_TABLE)))
    print("data_source 分布:", reader().execute(_SQL_LINEAGE_DIST.format(table=RECALC_TABLE)))
    return 0


GATE_KEYS: Final = ("coverage", "point_value_violations", "chain_health", "legacy_diff_quantified")


def cmd_swap(args: argparse.Namespace) -> int:
    """原子换名：前置=对拍报告 gates 四项全真（缺报告即拒绝，绝不"顺手换名"）。"""
    import json
    import os

    rep = args.report or os.path.join(".runtime/tmp/st-metaq-gc-20260924/wo004", "verify_latest.json")
    if not os.path.exists(rep):
        print(f"[abort] 对拍报告不存在：{rep}（先跑 verify_hfq.py 产出 --json）")
        return 2
    data = json.load(open(rep, encoding="utf-8"))
    bad = [k for k in GATE_KEYS if not data.get("gates", {}).get(k)]
    if bad:
        print(f"[abort] 对拍未全绿：{bad} —— 不换名、保留现场（宪法 §1 RULE-DATA-OPS 三步验证）")
        return 2
    if table_exists(LEGACY_TABLE):
        print(f"[abort] {LEGACY_TABLE} 已存在（先人工确认历史留存表语义再动）")
        return 2
    if not table_exists(RECALC_TABLE):
        print("[abort] 重算表不存在")
        return 2
    print(f"[gates] {data['gates']}  point_value_violations={data.get('metrics', {}).get('pv_violations')}")
    if not args.yes:
        print(f"[dry] RENAME {HFQ_TABLE} → {LEGACY_TABLE}, {RECALC_TABLE} → {HFQ_TABLE}（加 --yes 落地）")
        return 0
    wclient().execute(_SQL_SWAP_RENAME.format(hfq=HFQ_TABLE, legacy=LEGACY_TABLE, recalc=RECALC_TABLE))
    print(f"[swapped] 旧表留存为 {LEGACY_TABLE}；回滚 = --rollback --yes")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    if not table_exists(LEGACY_TABLE):
        print(f"[abort] {LEGACY_TABLE} 不存在，无可回滚")
        return 2
    if not args.yes:
        print(f"[dry] RENAME {HFQ_TABLE} → {RECALC_TABLE}, {LEGACY_TABLE} → {HFQ_TABLE}（加 --yes 落地）")
        return 0
    wclient().execute(_SQL_ROLLBACK_RENAME.format(hfq=HFQ_TABLE, recalc=RECALC_TABLE, legacy=LEGACY_TABLE))
    print("[rolled back] 现表已复位为换名前内容（重算表退回 _recalc 名待查）")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    """①/③ 落地腿：把重算表按窗提升进生产（幂等补齐 + 逐出非裁定口径），不整表换名。

    与 --swap 的分工：--swap=一次性整表换代（建新表+原子换名，存量口径换代用）；
    --promote=按日/按窗例行提升（日更腿与下游派生用），幂等可重跑，且因生产表已带
    lineage_version（③），逐出前 FINAL 也已由版本列判裁定口径赢 ⇒ 不存在"读到厂商值"的窗。
    """
    if not table_exists(RECALC_TABLE):
        print("[abort] 重算表不存在——先 --create/--run 生成待提升窗")
        return 2
    if not int(scalar(_SQL_HAS_LINEAGE_COL.format(tbl=HFQ_TABLE.split(".")[1]), 0)):
        print("[abort] 生产表缺 lineage_version 列（③ 版本列未落地）⇒ 无法保证提升后去重确定，拒绝")
        return 2
    hi = args.end or dt.date.fromisoformat(str(scalar(_SQL_MAX_TRADE_DATE.format(table=RECALC_TABLE))))
    lo = args.start or hi
    kw = dict(recalc=RECALC_TABLE, hfq=HFQ_TABLE, lo=d(lo), hi=d(hi), ver=CANON_LINEAGE_VERSION)
    pending = int(scalar(_SQL_PROMOTE_PENDING.format(**kw), 0))
    stale = int(scalar(_SQL_PROMOTE_STALE.format(**kw), 0))
    print(f"[promote] 窗 {d(lo)}..{d(hi)}  待补键={pending}  窗内非裁定口径行={stale}")
    if not args.yes:
        print("[dry] INSERT 补齐 → ALTER DELETE 逐出（加 --yes 落地）")
        print("   ·", _SQL_PROMOTE_FILL.format(**kw)[:150])
        print("   ·", _SQL_PROMOTE_EVICT.format(**kw)[:150])
        return 0
    c = wclient()
    if pending:
        c.execute(_SQL_PROMOTE_FILL.format(**kw), settings=_SETTINGS)
    if stale:
        c.execute(_SQL_PROMOTE_EVICT.format(**kw), settings={"mutations_sync": 2})
    print("[verify] 窗内 (version, source) 分布:", reader().execute(_SQL_PROMOTE_WINDOW.format(**kw)))
    print("[verify] 窗内同键多行(应 0，>1 仅当同口径自叠):", int(scalar(_SQL_PROMOTE_DUPKEYS.format(**kw), 0)))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="WO-004 kline_daily_hfq 重算管线（可逆路径：建表→灌数→对拍→换名）")
    p.add_argument("--create", action="store_true", help="建同构重算表")
    p.add_argument("--force", action="store_true", help="允许 DROP 重建重算表（只碰重算表）")
    p.add_argument("--run", action="store_true", help="分月灌数")
    p.add_argument("--status", action="store_true", help="进度与行数")
    p.add_argument("--swap", action="store_true", help="原子换名（需对拍全绿 + --yes）")
    p.add_argument("--promote", action="store_true", help="按窗提升进生产（幂等补齐+逐出非裁定口径，需 --yes）")
    p.add_argument("--rollback", action="store_true", help="反向换名（需 --yes）")
    p.add_argument("--start", type=dt.date.fromisoformat, default=None)
    p.add_argument("--end", type=dt.date.fromisoformat, default=None)
    p.add_argument("--resume", action="store_true", help="跳过已有分片月")
    p.add_argument("--limit-months", type=int, default=0, help="试跑：最多执行 N 片")
    p.add_argument("--echo-every", type=int, default=12)
    p.add_argument("--yes", action="store_true", help="确认换名/回滚/提升类动作落地")
    p.add_argument("--report", default=None, help="对拍报告 JSON 路径（--swap 前置读取）")
    a = p.parse_args(argv)
    if [a.create, a.run, a.status, a.swap, a.promote, a.rollback].count(True) != 1:
        p.error("必须且只能指定一个动作：--create/--run/--status/--swap/--promote/--rollback")
    if a.create:
        return cmd_create(a)
    if a.run:
        return cmd_run(a)
    if a.status:
        return cmd_status(a)
    if a.swap:
        return cmd_swap(a)
    if a.promote:
        return cmd_promote(a)
    return cmd_rollback(a)


if __name__ == "__main__":
    raise SystemExit(main())
