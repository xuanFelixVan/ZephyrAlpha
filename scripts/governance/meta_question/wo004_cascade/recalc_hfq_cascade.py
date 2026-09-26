# [BLUEPRINT] MOD-WO004-CASCADE-HFQ-RECALC | docs/_working/meta_question_answers/casefiles/HFQ-CASCADE.yaml
# [MODULE] scripts.governance.meta_question.wo004_cascade.recalc_hfq_cascade
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts.governance/meta_question/wo004/recalc_hfq.py（只读引用：日线血统标记/日期工具，禁造第二套口径）; zephyr.infrastructure.database_service (reader 对拍复核); zephyr.data.ch_writer (writer 通道 get_client); zephyr.data.table_registry (表名品类真源 #ARCH-CH-024)
# [CONSUMERS] scripts/governance/meta_question/wo004_cascade/verify_hfq_cascade.py（换名前置门的产出者）； scripts/governance/meta_question/wo004_cascade/sample_check_hfq_cascade.py（月度抽检复用本件常量）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 可逆性三步铁律（宪法 §1 RULE-DATA-OPS 破坏性 DB 操作三步验证）： 必要性=日线已按裁定改基座而周/月级联表未跟进，同项目两套 hfq 对 71.77% 标的互斥（双真源冲突，非待优化项）； 真实性=本件全部数字取自 CH 实测，聚合规则先由 verify 件 --derive 用"旧日线+该规则复现现周线"证伪通过； 可逆性=①只建同构新表 *_recalc ②对拍全绿才 --swap 原子换名 ③旧表整张改名 *_legacy_20260924 留存 ④--rollback 反向 RENAME 零数据丢失——全程**无一条 UPDATE/DELETE/TRUNCATE**，既有表零原地覆写； 口径零改动：价格真源 = 已裁定的 c1_market.kline_daily_hfq（raw×adj_factor），本件只做级联聚合， 不新增/不放宽任何阈值，链式衍生列（amplitude/pct_change/change/turnover）沿用现表 0 值约定 （实测现周/月表四列 100% 为 0，与 WO-004 决策 D5 同构）； 聚合规则（实测反推，非推测）：周=ISO 周（周一~周日）窗、月=自然月窗； open=窗首交易日 open（argMin by trade_date）、close=窗末交易日 close、high=max、low=min、 volume=sum、amount=sum、trade_date=窗内**末**交易日； 日线去重优先级：同 (symbol, trade_date) 双行时取"血统为 recalc_raw_x_adjfactor 者优先、其次 ingest_ts 最新" ——日线表在换名后被采集器回灌了 803+803 行旧口径 bdpan_hfq（600510 2026-09-23 差 12.9%）， 级联若按末写优先会把被裁定为错的基座继续下传；无歧义键（99.98% 行）本规则与末写优先同值； 分片幂等：按自然年 ALTER ... DROP PARTITION + INSERT 重灌，中断可续跑，无双写残留； 月窗分片缓冲 14 日 > ISO 周跨度 7 日 ⇒ 任一"末交易日落在本年"的周 bar 其整周日线必在窗内， 被缓冲截断的周 bar 其末交易日必落在缓冲带（被 toYear 过滤剔除）⇒ 分片结果与全表一次聚合逐位等值； fail-visible：任一分片异常即抛出终止并保留现场（不 swap）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 建表/分片 INSERT 失败→抛出并终止（已灌分片保留，重跑先 DROP PARTITION 再灌）； --swap 前置=读对拍报告 JSON 的 gates 全真，缺报告/未全绿一律拒绝换名并退出码 2； 换名单条 RENAME 同时原子覆盖周、月两表（不出现"周已换月未换"的半程态）。
# [TESTS] 无 pytest（一次性运维管线，同族 wo004/recalc_hfq.py 先例）； 验收=verify_hfq_cascade.py 五闸数字（周↔日、月↔日、偏序、volume 守恒、覆盖不缩水）。
# [A_module] module_id=MOD-WO004-CASCADE-HFQ-RECALC | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""recalc_hfq_cascade — 后复权周/月线按已修正日线重算（WO-004 级联补做，双真源冲突治本）。

缺陷：WO-004 按裁定把 c1_market.kline_daily_hfq 重算为 raw×adj_factor 并原子换名后，
级联表 kline_weekly_hfq / kline_monthly_hfq 仍由采集器（tasks.yaml: kline_weekly_hfq_incremental，
"miniQMT 后复权日K聚合"）在**被判定为错的旧基座**上续算 ⇒ 周线末收盘 vs 新日线末收盘不符率
71.77%（3,748/5,222），vs 旧日线仅 5.65%。同一项目两张表对 72% 标的给出互相矛盾的后复权价。

本件只做一件事：把日线已裁定的口径补做到级联层，路径与 wo004 完全同构
（建新表→对拍全绿→原子换名→旧表整张留存→可回滚）。

用法（顺序即验收顺序，禁跳步）：
    python scripts/governance/meta_question/wo004_cascade/recalc_hfq_cascade.py --create
    python scripts/governance/meta_question/wo004_cascade/recalc_hfq_cascade.py --run [--resume] [--only weekly]
    python scripts/governance/meta_question/wo004_cascade/recalc_hfq_cascade.py --status
    python scripts/governance/meta_question/wo004_cascade/verify_hfq_cascade.py --derive      # 先证聚合规则
    python scripts/governance/meta_question/wo004_cascade/verify_hfq_cascade.py --json .../verify_latest.json
    python scripts/governance/meta_question/wo004_cascade/recalc_hfq_cascade.py --swap --yes
    python scripts/governance/meta_question/wo004_cascade/recalc_hfq_cascade.py --rollback --yes
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from typing import Final

_DIR = os.path.dirname(os.path.abspath(__file__))
_WO004_DIR = os.path.join(os.path.dirname(_DIR), "wo004")
for _p in (_DIR, _WO004_DIR, "src", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import importlib.util as _ilu  # noqa: E402

_spec_rc = _ilu.spec_from_file_location("recalc_hfq", os.path.join(_WO004_DIR, "recalc_hfq.py"))
RC = _ilu.module_from_spec(_spec_rc)
_spec_rc.loader.exec_module(RC)  # （只读引用：日线血统标记与日期工具的唯一真源，禁第二套）

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

# ------------------------------------------------------------ 表名常量（唯一真源=品类册，对拍/抽检同引）
DAILY_HFQ: Final = RC.HFQ_TABLE  # c1_market.kline_daily_hfq
DAILY_HFQ_LEGACY: Final = RC.LEGACY_TABLE  # 旧基座（仅用于规则反推）
# 旁挂表 *_recalc / *_legacy_20260924 是本管线自建的影子表、不在品类册内，故一律由已注册
# 基表派生（#ARCH-CH-024：禁把自建表名塞进 TableRegistry，品类真源唯一 ⇒ 衍生名可证）。
WEEKLY_TABLE: Final = get_registry().table("market_kline_weekly_hfq")
WEEKLY_RECALC: Final = f"{WEEKLY_TABLE}_recalc"
WEEKLY_LEGACY: Final = f"{WEEKLY_TABLE}_legacy_20260924"
MONTHLY_TABLE: Final = get_registry().table("market_kline_monthly_hfq")
MONTHLY_RECALC: Final = f"{MONTHLY_TABLE}_recalc"
MONTHLY_LEGACY: Final = f"{MONTHLY_TABLE}_legacy_20260924"

# ------------------------------------------------------------ 口径常量（实测钉死，勿改）
LINEAGE_MARK: Final = RC.DATA_SOURCE_MARK  # 日线血统 'recalc_raw_x_adjfactor'（优先键）
WEEK_MARK: Final = "recalc_weekly_from_daily_hfq"  # 级联自证标记：与 WO-004 同法（不复用 'bdpan_hfq' 假标记）
MONTH_MARK: Final = "recalc_monthly_from_daily_hfq"
WEEK_BUFFER_DAYS: Final = 14  # 周窗分片缓冲（> ISO 周跨度 7 日，见 [INVARIANTS] 证明）

INSERT_COLS: Final = (
    "trade_date, symbol, open, close, high, low, volume, amount, amplitude, pct_change, change, turnover, data_source"
)

_SETTINGS: Final = {"max_execution_time": 0, "connect_timeout": 10, "output_format_write_statistics": 0}

# 两张级联表的差异只在"窗"与"标记"，其余管线共用 —— 用配置表驱动，禁复制第二份灌数逻辑
TARGETS: Final = {
    "weekly": {
        "live": WEEKLY_TABLE,
        "recalc": WEEKLY_RECALC,
        "legacy": WEEKLY_LEGACY,
        "mark": WEEK_MARK,
        "unit": "iso_week",
        "buffer_days": WEEK_BUFFER_DAYS,
    },
    "monthly": {
        "live": MONTHLY_TABLE,
        "recalc": MONTHLY_RECALC,
        "legacy": MONTHLY_LEGACY,
        "mark": MONTH_MARK,
        "unit": "calendar_month",
        "buffer_days": 0,
    },
}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。全部语句以 {} 占位承载表名/口径值与运行期日期窗，
# 由调用点 .format() 注入——常量内禁落任何日期字面量。
_SQL_DAILY_DEDUP = (
    "SELECT symbol, trade_date, "
    "  argMax(open, ordk) AS o, argMax(close, ordk) AS c, "
    "  argMax(high, ordk) AS h, argMax(low, ordk) AS l, "
    "  argMax(volume, ordk) AS v, argMax(amount, ordk) AS a "
    "FROM (SELECT symbol, trade_date, open, close, high, low, volume, amount, "
    "        (if(data_source = '{mark}', 1, 0), ingest_ts) AS ordk "
    "      FROM {daily} WHERE trade_date BETWEEN '{lo}' AND '{hi}') "
    "GROUP BY symbol, trade_date"
)
_SQL_BARS_WEEKLY = (
    "SELECT symbol, toISOYear(trade_date) AS uy, toISOWeek(trade_date) AS uw, "
    "  max(trade_date) AS td, argMin(o, trade_date) AS o, argMax(c, trade_date) AS c, "
    "  max(h) AS h, min(l) AS l, sum(v) AS v, sum(a) AS a "
    "FROM ({daily}) GROUP BY symbol, uy, uw"
)
_SQL_BARS_MONTHLY = (
    "SELECT symbol, toYear(trade_date) AS uy, toMonth(trade_date) AS uw, "
    "  max(trade_date) AS td, argMin(o, trade_date) AS o, argMax(c, trade_date) AS c, "
    "  max(h) AS h, min(l) AS l, sum(v) AS v, sum(a) AS a "
    "FROM ({daily}) GROUP BY symbol, uy, uw"
)
_SQL_SHARD_INSERT = (
    "INSERT INTO {recalc} ({cols}) "
    "SELECT td AS trade_date, symbol, o AS open, c AS close, h AS high, l AS low, "
    "  toUInt64(v) AS volume, CAST(round(a, 2) AS Decimal(18, 2)) AS amount, "
    "  toDecimal64(0, 4) AS amplitude, toDecimal64(0, 4) AS pct_change, "
    "  toDecimal64(0, 4) AS change, toDecimal64(0, 4) AS turnover, "
    "  '{mark}' AS data_source "
    "FROM ({bars}) WHERE toYear(td) = {y}"
)
_SQL_DROP_TABLE = "DROP TABLE {recalc}"
_SQL_CREATE_LIKE = (
    "CREATE TABLE {recalc} AS {live} "
    "ENGINE = ReplacingMergeTree "
    "PARTITION BY toYYYYMM(trade_date) "
    "ORDER BY (symbol, trade_date)"
)
_SQL_TABLE_EXISTS = "SELECT count() FROM system.tables WHERE database='{db}' AND name='{tbl}'"
_SQL_TABLE_KEYS = (
    "SELECT engine, sorting_key, partition_key FROM system.tables WHERE database='c1_market' AND name='{name}'"
)
_SQL_TABLE_COLUMNS = (
    "SELECT name,type,default_kind,default_expression FROM system.columns "
    "WHERE database='c1_market' AND table='{name}' ORDER BY position"
)
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"
_SQL_MIN_TRADE_DATE = "SELECT min(trade_date) FROM {table}"
_SQL_MIN_TRADE_DATE = "SELECT min(trade_date) FROM {table}"
_SQL_COUNT_IN_YEAR = "SELECT count() FROM {table} WHERE toYear(trade_date) = {y}"
_SQL_YEARS_PRESENT = "SELECT DISTINCT toYear(trade_date) FROM {table}"
_SQL_PART_ACTIVE = (
    "SELECT DISTINCT partition_id FROM system.parts WHERE database='c1_market' AND table='{name}' AND active=1"
)
_SQL_ALTER_DROP_PARTITION = "ALTER TABLE {recalc} DROP PARTITION {ym}"
_SQL_STATUS_AGG = (
    "SELECT count(), uniqExact(symbol), min(trade_date), max(trade_date), "
    "countDistinct(toYYYYMM(trade_date)) FROM {table}"
)
_SQL_UNIQUE_KEYS = "SELECT uniqExact((symbol,trade_date)) FROM {table}"
_SQL_LINEAGE_DIST = "SELECT data_source, count() FROM {table} GROUP BY data_source ORDER BY 2 DESC"
_SQL_SWAP_PAIRS = "RENAME TABLE {pairs}"


def d(x: dt.date) -> str:
    return RC.d(x)


# ------------------------------------------------------------ 真源表达式：日线去重腿
def sql_daily_src(lo: dt.date, hi: dt.date, daily: str = DAILY_HFQ, mark: str = LINEAGE_MARK) -> str:
    """日线按 (symbol, trade_date) 唯一化：血统优先（裁定口径）→ ingest_ts 次新。

    实测：换名后采集器把 803 行旧口径 bdpan_hfq 回灌到 2026-09-23（与 recalc 行同键，
    600510 close 39.2219 vs 45.0247 差 12.9%）——纯末写优先会让被裁定为错的基座继续下传。
    """
    return _SQL_DAILY_DEDUP.format(mark=mark, daily=daily, lo=d(lo), hi=d(hi))


def sql_bars(daily_sql: str, unit: str) -> str:
    tpl = _SQL_BARS_WEEKLY if unit == "iso_week" else _SQL_BARS_MONTHLY
    return tpl.format(daily=daily_sql)


def shard_sql(year: int, cfg: dict, src_lo: dt.date, src_hi: dt.date, daily: str = DAILY_HFQ) -> str:
    """单年灌数 SQL：日线去重 → 窗聚合 → 只保留末交易日落在本年的 bar（分片互斥且完备）。"""
    daily_sql = sql_daily_src(src_lo, src_hi, daily=daily)
    return _SQL_SHARD_INSERT.format(
        recalc=cfg["recalc"], cols=INSERT_COLS, mark=cfg["mark"], bars=sql_bars(daily_sql, cfg["unit"]), y=year
    )


# ------------------------------------------------------------ 分片调度
def year_window(year: int, buffer_days: int) -> tuple[dt.date, dt.date]:
    lo = dt.date(year, 1, 1) - dt.timedelta(days=buffer_days)
    hi = dt.date(year, 12, 31) + dt.timedelta(days=buffer_days)
    return lo, hi


def shard_plan(src_lo: dt.date, src_hi: dt.date) -> list[int]:
    return list(range(src_lo.year, src_hi.year + 1))


# ------------------------------------------------------------ 连接（模块级缓存）
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
    return rows[0][0]


def table_exists(name: str) -> bool:
    db, tbl = name.split(".")
    return bool(scalar(_SQL_TABLE_EXISTS.format(db=db, tbl=tbl), 0))


def src_domain(daily: str = DAILY_HFQ) -> tuple[dt.date, dt.date]:
    lo = dt.date.fromisoformat(str(scalar(_SQL_MIN_TRADE_DATE.format(table=daily))))
    hi = dt.date.fromisoformat(str(scalar(_SQL_MAX_TRADE_DATE.format(table=daily))))
    return lo, hi


# ------------------------------------------------------------ 子命令
def cmd_create(args: argparse.Namespace) -> int:
    c = wclient()
    for key, cfg in TARGETS.items():
        if args.only and args.only != key:
            continue
        if table_exists(cfg["recalc"]):
            if not args.force:
                print(f"[skip] {cfg['recalc']} 已存在（--force 才允许 DROP 重建；现表永不受本件影响）")
                continue
            print(f"[drop] {cfg['recalc']}")
            c.execute(_SQL_DROP_TABLE.format(recalc=cfg["recalc"]))
        _create_like(c, cfg)
    return 0


def _create_like(c, cfg: dict) -> None:
    ddl = _SQL_CREATE_LIKE.format(recalc=cfg["recalc"], live=cfg["live"])
    print(f"[ddl] {ddl}")
    c.execute(ddl)
    short = cfg["recalc"].split(".")[1]
    got = reader().execute(_SQL_TABLE_KEYS.format(name=short))
    src = reader().execute(_SQL_TABLE_KEYS.format(name=cfg["live"].split(".")[1]))
    print(f"[check] recalc={got[0]}\n[check] live  ={src[0]}")
    cols_r = reader().execute(_SQL_TABLE_COLUMNS.format(name=short))
    cols_s = reader().execute(_SQL_TABLE_COLUMNS.format(name=cfg["live"].split(".")[1]))
    if got[0] != src[0] or cols_r != cols_s:
        raise RuntimeError(f"重算表与现表不同构：engine/keys={got[0] != src[0]} cols={len(cols_r)}/{len(cols_s)}")
    print(f"[ok] 同构确认：{len(cols_r)} 列全等（含 exchange/symbol_canonical MATERIALIZED 派生列）")


def cmd_run(args: argparse.Namespace) -> int:
    c = wclient()
    daily = DAILY_HFQ
    lo, hi = src_domain(daily)
    if args.start:
        lo = max(lo, args.start)
    if args.end:
        hi = min(hi, args.end)
    years = shard_plan(lo, hi)
    for key, cfg in TARGETS.items():
        if args.only and args.only != key:
            continue
        if not table_exists(cfg["recalc"]):
            print(f"[abort] {cfg['recalc']} 不存在——先 --create")
            return 2
        _run_one(c, cfg, daily, lo, hi, years, args)
    return 0


def _run_one(c, cfg: dict, daily: str, lo: dt.date, hi: dt.date, years: list[int], args: argparse.Namespace) -> None:
    short = cfg["recalc"].split(".")[1]
    have = {int(r[0]) for r in reader().execute(_SQL_YEARS_PRESENT.format(table=cfg["recalc"]))}
    todo = [y for y in years if y not in have] if args.resume else years
    print(
        f"[run:{cfg['unit']}] 源窗 {d(lo)}..{d(hi)} 分片 {len(years)} 自然年，"
        f"已存在 {len(have & set(years))}，本次执行 {len(todo)}"
    )
    parts = {str(r[0]) for r in reader().execute(_SQL_PART_ACTIVE.format(name=short))}
    buf = dt.timedelta(days=cfg["buffer_days"])
    t0 = dt.datetime.now()
    total = 0
    for i, y in enumerate(todo, 1):
        for m in range(1, 13):
            pid = f"{y}{m:02d}"
            if pid in parts:
                c.execute(_SQL_ALTER_DROP_PARTITION.format(recalc=cfg["recalc"], ym=pid))
        wlo, whi = year_window(y, cfg["buffer_days"])
        c.execute(shard_sql(y, cfg, max(wlo, lo - buf), min(whi, hi + buf), daily), settings=_SETTINGS)
        n = int(scalar(_SQL_COUNT_IN_YEAR.format(table=cfg["recalc"], y=y), 0))
        total += n
        if i % args.echo_every == 0 or i == len(todo):
            el = (dt.datetime.now() - t0).total_seconds()
            print(f"  [{i}/{len(todo)}] {y} rows={n} 累计={total} 用时={el:.0f}s")
        if args.limit_shards and i >= args.limit_shards:
            print(f"  [stop] --limit-shards={args.limit_shards} 试跑截止")
            break
    print(f"[done:{short}] 覆盖 {total} 行 / {len(todo)} 片（幂等可续跑：--resume 跳过已有年）")


def cmd_status(args: argparse.Namespace) -> int:
    q = _SQL_STATUS_AGG
    for key, cfg in TARGETS.items():
        if args.only and args.only != key:
            continue
        for role, tbl in (("recalc", cfg["recalc"]), ("live ", cfg["live"])):
            if not table_exists(tbl):
                print(f"[status:{key}] {role} {tbl} 不存在")
                continue
            agg = tuple(reader().execute(q.format(table=tbl))[0])
            uniq = scalar(_SQL_UNIQUE_KEYS.format(table=tbl))
            print(
                f"[status:{key}] {role} {tbl}\n    rows/syms/min/max/months={agg} uniq_key={uniq}"
                f" dup={int(agg[0]) - int(uniq)}"
            )
            print("    data_source:", reader().execute(_SQL_LINEAGE_DIST.format(table=tbl))[:4])
    print(f"[status] 日线源 {DAILY_HFQ} 域={src_domain()}")
    return 0


def gate_report(path: str) -> dict:
    import json

    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_swap(args: argparse.Namespace) -> int:
    """原子换名：周、月两表在**同一条** RENAME 里完成（禁半程态）；前置=对拍全绿。"""
    rep = args.report or os.path.join(".runtime/tmp/st-metaq-gc-20260924/hfq_cascade", "verify_latest.json")
    try:
        data = gate_report(rep)
    except FileNotFoundError:
        print(f"[abort] 对拍报告不存在：{rep}（先跑 verify_hfq_cascade.py --json）")
        return 2
    gates = data.get("gates", {})
    bad = [k for k, v in gates.items() if not v]
    if not gates or bad:
        print(f"[abort] 对拍未全绿：{bad or '空报告'} —— 不换名、保留现场（宪法 §1 RULE-DATA-OPS 三步验证）")
        return 2
    for key, cfg in TARGETS.items():
        if table_exists(cfg["legacy"]):
            print(f"[abort] {cfg['legacy']} 已存在（先人工确认历史留存表语义再动）")
            return 2
        if not table_exists(cfg["recalc"]):
            print(f"[abort] {cfg['recalc']} 不存在")
            return 2
    print(f"[gates] {gates}")
    pairs = ", ".join(f"{cfg['live']} TO {cfg['legacy']}, {cfg['recalc']} TO {cfg['live']}" for cfg in TARGETS.values())
    if not args.yes:
        print(f"[dry] RENAME TABLE {pairs}（加 --yes 落地）")
        return 0
    wclient().execute(_SQL_SWAP_PAIRS.format(pairs=pairs))
    print(f"[swapped] 旧表留存为 {WEEKLY_LEGACY} / {MONTHLY_LEGACY}；回滚 = --rollback --yes")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    pairs = []
    for cfg in TARGETS.values():
        if not table_exists(cfg["legacy"]):
            print(f"[abort] {cfg['legacy']} 不存在，无可回滚")
            return 2
        pairs.append(f"{cfg['live']} TO {cfg['recalc']}, {cfg['legacy']} TO {cfg['live']}")
    if not args.yes:
        print(f"[dry] RENAME TABLE {', '.join(pairs)}（加 --yes 落地）")
        return 0
    wclient().execute(_SQL_SWAP_PAIRS.format(pairs=", ".join(pairs)))
    print("[rolled back] 现表已复位为换名前内容（重算表退回 _recalc 名待查）")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="WO-004 级联：后复权周/月线按已修正日线重算（可逆路径：建表→灌数→对拍→换名）"
    )
    p.add_argument("--create", action="store_true", help="建同构重算表")
    p.add_argument("--force", action="store_true", help="允许 DROP 重建重算表（只碰重算表）")
    p.add_argument("--run", action="store_true", help="分年灌数")
    p.add_argument("--status", action="store_true", help="进度与行数")
    p.add_argument("--swap", action="store_true", help="原子换名（需对拍全绿 + --yes）")
    p.add_argument("--rollback", action="store_true", help="反向换名（需 --yes）")
    p.add_argument("--only", choices=["weekly", "monthly"], default=None)
    p.add_argument("--start", type=dt.date.fromisoformat, default=None)
    p.add_argument("--end", type=dt.date.fromisoformat, default=None)
    p.add_argument("--resume", action="store_true", help="跳过已灌年份")
    p.add_argument("--limit-shards", type=int, default=0, help="试跑：最多执行 N 片")
    p.add_argument("--echo-every", type=int, default=5)
    p.add_argument("--yes", action="store_true", help="确认换名/回滚类动作落地")
    p.add_argument("--report", default=None, help="对拍报告 JSON 路径（--swap 前置读取）")
    a = p.parse_args(argv)
    if [a.create, a.run, a.status, a.swap, a.rollback].count(True) != 1:
        p.error("必须且只能指定一个动作：--create/--run/--status/--swap/--rollback")
    if a.create:
        return cmd_create(a)
    if a.run:
        return cmd_run(a)
    if a.status:
        return cmd_status(a)
    if a.swap:
        return cmd_swap(a)
    return cmd_rollback(a)


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 级联重算器是人工点火的存量修复作业（带 dry-run 与回滚口），非常驻自动任务
    raise SystemExit(main())
