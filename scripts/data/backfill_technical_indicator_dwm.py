# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] scripts.data.backfill_technical_indicator_dwm
# [DOMAIN] D_DATA
# [A_module] module_id=scripts-data-ti-dwm-backfill | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.implementations.internal_compute_provider; zephyr.data.provider_base
# [CONSUMERS] tilib_indicator_backfill_nightly（02:30 经 backfill_night.ps1→tilib_dwm_shard_runner 分片调用）；Owner/施工会话手动补数
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 单进程串行分片（并发=内存总闸 Code 241）；ReplacingMergeTree 同键 (symbol,period,trade_time) 覆盖幂等可重跑；BufferedWriter 批量写（max_seconds=30）；dry-run 不落库；
#  值级跳过（P1）＝同键最新版逐列相对差 ≤1e-9 不 INSERT，判据常量 _VALUE_SKIP_REL_TOL，任何取不到比对基的情形一律退回全量写（宁多写不漏写）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FetchResult.error 或 BufferedWriter.add/flush 失败即 RuntimeError 非零退出；单片失败不污染其他分片（子进程隔离）；比对基现读失败仅告警并退回全量写（不静默少写）
# [TESTS] 本 CLI 以 --help 与 --dry-run 自测；指标正确性由 tests/zephyr/factor/technical_indicators/ 全套件守卫；值级跳过判据由 tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py 钉（含 1e-6 必写/1e-13 必跳双向红证）
# noqa: m11-perm-manual-legitimate  tilib_indicator_backfill_nightly 02:30 夜跑分片子进程自动调用（backfill_night.ps1→runner 链），兼手动补数运维件，人工触发是设计意图非缺陷
"""日/周/月技术指标历史回填器（16 号设计文档 §7⑥，2026-09-14 探针发现）。

背景：
    c1_market.technical_indicator 的 daily/weekly/monthly 数据起点=2026-08（调度闭环日），
    仅 ~1 个月历史；而 30/60/120min 有 5 年。根因=scheduler._compute_start_date 对
    incremental=False 任务返回"当月 1 号"——technical_indicator_full_refresh 实为月初校准，
    无历史回填能力。本脚本走生产 provider→BufferedWriter 同链路补齐。

范围裁定（本脚本默认值）：
    daily   2021-01-01 起（表合同 valid_since=2021-09-01，预留 MA60/bias_24 等预热跑道）
    weekly  2019-01-01 起（kline_weekly 源下界）
    monthly 2019-01-01 起（kline_monthly 源下界）

幂等性：ReplacingMergeTree 同键 (symbol, period, trade_time) 覆盖式更新，可安全重跑。
但"覆盖"在引擎里没有版本列时并不免费——每晚重灌会把同键版本数堆到 7 版、行数按趟数涨
（2026-10-09 实测 daily 段 23,112,162 行 / 8,925,969 键）。故写前加值级跳过：与当前可见
最新版逐列比相对差，全部 ≤1e-9 就不 INSERT（判据常量 _VALUE_SKIP_REL_TOL，执行体 value_skip_batch）。

用法：
    python scripts/data/backfill_technical_indicator_dwm.py                # 三周期默认范围
    python scripts/data/backfill_technical_indicator_dwm.py --periods daily --dry-run
    python scripts/data/backfill_technical_indicator_dwm.py --start-daily 2020-01-01
    python scripts/data/backfill_technical_indicator_dwm.py --no-value-skip  # 回滚位（旧行为）

运维红线：
    长批任务先登记 data/runtime/process_reaper_keep.txt（子串 backfill_technical_indicator_dwm）。
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import re
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Final

# provider 懒加载 schemas.categories.*（DDL-as-Code 真源），需 repo root 在 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# src 前插：editable install 把 zephyr 钉在主区 src，worktree 运行必须显式抢优先级
_REPO_SRC = _REPO_ROOT / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from zephyr.data.buffered_writer import BufferedWriter
from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
from zephyr.data.provider_base import FetchPayload, FetchResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ti-dwm-backfill")

from zephyr.data.table_registry import get_registry

TABLE = get_registry().table("market_technical_indicator")
_DEFAULT_STARTS = {
    "daily": "2021-01-01",
    "weekly": "2019-01-01",
    "monthly": "2019-01-01",
}

# ── 值级跳过（dexp 战役 00 号文 §11 P1，Owner 2026-10-09 批复认这个阈值）────────────────
# 根因：夜跑每晚把 daily 全史重灌，同键版本最多叠到 7 版（实测 23,112,162 行 / 8,925,969 键
# =2.59× 行膨胀），而版本之间实测只差浮点末位（绝对差 ≤9.1e-13，量级 130-143）。
# 判据：与"该键当前可见最新版"逐列比相对差，全部列 ≤ 本阈值 ⇒ 整行不 INSERT。
_VALUE_SKIP_REL_TOL: Final = 1e-9
# 相对差在 |old|≈0 处不闭合，给一个极小的绝对下限护分母。取 1e-12 使阈值仍随 |old|
# 线性缩放（不变成绝对阈值），方向后果偏保守：近零列更容易判"变了"⇒ 照写，不会漏写。
_REL_DENOM_FLOOR: Final = 1e-12
# 键列/元数据列不参与比对（trade_time 两侧先归一到日粒度字符串，data_source 非指标数值）
_NON_COMPARED_COLUMNS: Final = frozenset({"trade_date", "trade_time", "symbol", "period", "data_source", "ingest_ts"})
# 单批比对基上限（标的数 × 日跨度）：provider 实测每批=个位标的 × 数十行，正常远不触及；
# 触及即说明批形变了，放弃本批预判退回全量写，并把该批计入 degraded 度量（不静默）。
_MAX_BASE_KEYS: Final = 200_000
# 连续取不到比对基多少次就熔断停用值级跳过（本程内不再尝试）。
# 每次失败的代价≈一轮 TCP+HTTP 重试 50s（2026-10-10 实测 Code 241），一个 250 批的片若
# 批批重试＝把夜跑从 21 分钟/片拖成几小时/片；熔断是"少省"，绝不因此"少写"。
_MAX_CONSECUTIVE_BASE_FAILURES: Final = 3
# 标识符白名单：列名/标的号只允许这个形状，否则拼进 SQL 就是注入口
_IDENT_PATTERN: Final = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_SYMBOL_PATTERN: Final = re.compile(r"^[A-Za-z0-9._\-]{1,32}$")
_NULL_TOKENS: Final = frozenset({"", "\\N", "NULL", "nullptr", "nan"})

_SQL_NUMERIC_COLUMNS = (
    "SELECT name FROM system.columns WHERE database = '{db}' AND table = '{tbl}' AND type = 'Nullable(Float64)'"
)
# 比对基查询形态（2026-10-10 三形态实测选定的唯一可用形）：
#   · 谓词必须直接落在 symbol + trade_time 范围上——PARTITION BY (period, toYYYYMM(trade_date))、
#     ORDER BY (symbol, period, trade_time)，写成 toDate(trade_time) BETWEEN 会让主键剪枝失效、
#     退化成全 daily 段扫（23M 行 × 最多 7 版 × 215 列），实测被 CH OvercommitTracker 判 Code 241。
#   · 不写 GROUP BY/argMax：215 个 argMax 聚合态同样爆内存（同夜实测）。表无版本列，
#     FINAL 幸存行即下游可见版，用它当比对基与"重写会不会改变读数"这个问题同构。
#   · 显式带 FINAL ⇒ ch_reader 的自动注入跳过本句（见 inject_final "已有 FINAL 则不重复注入"）。
_SQL_LATEST_WINDOW = (
    "SELECT symbol, toString(trade_time) AS day, {cols} "
    "FROM {table} FINAL "
    "WHERE period = '{period}' AND symbol IN ({symbols}) "
    "AND trade_time >= '{t_from}' AND trade_time < '{t_to}'"
)


def _to_float(raw: object) -> float | None:
    """CH TSV 单元 → float；NULL/空/不可解析一律 None（None 参与比对＝"这一侧缺值"）。"""
    if raw is None:
        return None
    text = str(raw).strip()
    if text in _NULL_TOKENS:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _norm_day(value: object) -> str:
    """日粒度键归一：dwm 三周期每行 trade_time 都是当日 00:00:00.000，两侧同尺才可比。"""
    return str(value)[:10]


def split_table_name(table: str) -> tuple[str, str]:
    """'db.tbl' → (db, tbl)；不带库名即判错（比对基查询必须有库名，system.columns 按库表取数）。"""
    db, _, tbl = table.partition(".")
    if not tbl:
        raise ValueError(f"表名缺库名前缀: {table!r}")
    return db, tbl


def numeric_indicator_columns(table: str) -> frozenset[str]:
    """现读本表 Nullable(Float64) 列集合＝可比值列全集（不硬编码列清单，防与 DDL 漂移）。"""
    from zephyr.data import ch_reader

    db, tbl = split_table_name(table)
    rows = ch_reader.query_rows(_SQL_NUMERIC_COLUMNS.format(db=db, tbl=tbl), timeout=30)
    return frozenset(str(r[0]) for r in rows)


def _build_latest_sql(
    table: str,
    period: str,
    symbols: list[str],
    day_from: str,
    day_to: str,
    value_cols: list[str],
) -> str:
    """组按批比对基查询。任何标识符不合法⇒抛错（绝不带可疑串进 SQL）。"""
    for col in value_cols:
        if not _IDENT_PATTERN.match(col):
            raise ValueError(f"非法列名: {col!r}")
    for sym in symbols:
        if not _SYMBOL_PATTERN.match(sym):
            raise ValueError(f"非法标的号: {sym!r}")
    datetime.date.fromisoformat(day_from)
    datetime.date.fromisoformat(day_to)
    cols = ", ".join(value_cols)
    sym_list = ", ".join(f"'{s}'" for s in symbols)
    return _SQL_LATEST_WINDOW.format(
        cols=cols,
        table=table,
        period=period,
        symbols=sym_list,
        t_from=f"{day_from} 00:00:00",
        # 右开边界＝末日 +1 天：范围剪枝可用，且不漏掉末日任何时刻的键
        t_to=(datetime.date.fromisoformat(day_to) + datetime.timedelta(days=1)).isoformat() + " 00:00:00",
    )


def fetch_base_for_batch(
    table: str,
    period: str,
    rows: list[tuple],
    columns: list[str],
    value_cols: list[str],
) -> dict[tuple[str, str], list[float | None]]:
    """现读本批 keys 的当前可见版指标值（键=(symbol, day)）。

    本批规模由 provider 决定（实测每批=个位标的 × 数十行），所以比对基本身是有界的——
    这是选"按批窄窗读"而不是"整片预取"的原因（整片预取在本表 215 列下客户端与
    服务端两头都撑不住，2026-10-10 实测）。
    """
    from zephyr.data import ch_reader

    idx = {name: i for i, name in enumerate(columns)}
    sym_i, tt_i = idx["symbol"], idx["trade_time"]
    days = [_norm_day(r[tt_i]) for r in rows]
    want_days = set(days)
    symbols = sorted({str(r[sym_i]) for r in rows})
    if not symbols or not want_days:
        return {}
    sql = _build_latest_sql(table, period, symbols, min(days), max(days), value_cols)
    fetched = ch_reader.query_rows(sql, timeout=300)
    out: dict[tuple[str, str], list[float | None]] = {}
    for row in fetched:
        key = (str(row[0]), _norm_day(row[1]))
        if key[1] not in want_days:
            continue
        out[key] = [_to_float(row[2 + j]) for j in range(len(value_cols))]
    return out


def row_rel_diverged(
    new_values: list[float | None],
    old_values: list[float | None],
    tol: float = _VALUE_SKIP_REL_TOL,
) -> bool:
    """逐列相对差判据：任一列 |new-old| > tol × max(|old|, 下限) ⇒ True（这行要写）。

    两侧同为 None＝同缺＝该列不判变；一侧有值一侧缺值＝判变（方向保守，照写）。
    """
    for new, old in zip(new_values, old_values, strict=False):
        if new is None and old is None:
            continue
        if new is None or old is None:
            return True
        if abs(new - old) > tol * max(abs(old), _REL_DENOM_FLOOR):
            return True
    return False


def split_unchanged_rows(
    rows: list[tuple],
    columns: list[str],
    stored: dict[tuple[str, str], list[float | None]],
    value_cols: list[str],
    tol: float = _VALUE_SKIP_REL_TOL,
) -> tuple[list[tuple], int]:
    """把一批行分成"必须写"与"值未变可跳"。键不在比对基＝新键＝必写。"""
    idx = {name: i for i, name in enumerate(columns)}
    sym_i, tt_i = idx["symbol"], idx["trade_time"]
    col_pos = [idx[name] for name in value_cols]
    kept: list[tuple] = []
    skipped = 0
    for row in rows:
        key = (str(row[sym_i]), _norm_day(row[tt_i]))
        old = stored.get(key)
        if old is None:
            kept.append(row)
            continue
        if row_rel_diverged([row[p] for p in col_pos], old, tol):
            kept.append(row)
        else:
            skipped += 1
    return kept, skipped


def resolve_compare_columns(columns: list[str], numeric_all: frozenset[str]) -> list[str]:
    """本批可比值列 = 批内列 ∩ 表内 Nullable(Float64) 列 − 键列/元数据列。"""
    return [c for c in columns if c in numeric_all and c not in _NON_COMPARED_COLUMNS]


def _neutral_stats(rows_in: int) -> dict:
    """ "本批没做比对"的中性度量：键齐全，调用方读任何键都不该 KeyError。

    （2026-10-10 测试抓到过一次真崩：兜底分支少给 base_keys 键，于是"比对基失灵"把
    夜跑打死——失灵的止血判据绝不能反过来成为故障源。）
    """
    return {
        "rows_in": rows_in,
        "skipped": 0,
        "base_keys": 0,
        "degraded": "",
        "uncompared_columns": [],
    }


def value_skip_batch(
    result: FetchResult,
    period: str,
    numeric_all: frozenset[str],
    table: str,
    tol: float = _VALUE_SKIP_REL_TOL,
) -> tuple[FetchResult | None, dict]:
    """按批做值级跳过。返回 (要写的 result，或 None=整批可跳, 本批度量)。

    读不到比对基时**不吞异常**，直接上抛给调用方记 degraded 并原样全量写：跳过判据失灵
    必须表现为"少省"，绝不能表现为"少写"（后者是静默数据缺失，比多写贵得多）。
    """
    idx = {name: i for i, name in enumerate(result.columns)}
    compare = resolve_compare_columns(result.columns, numeric_all)
    stats = _neutral_stats(len(result.rows))
    stats["uncompared_columns"] = [c for c in result.columns if c not in compare and c not in _NON_COMPARED_COLUMNS]
    if not compare:
        stats["degraded"] = "no-comparable-columns"
        return result, stats
    days = [_norm_day(row[idx["trade_time"]]) for row in result.rows]
    symbols = sorted({str(row[idx["symbol"]]) for row in result.rows})
    if len(symbols) * len(set(days)) > _MAX_BASE_KEYS:
        stats["degraded"] = f"batch-too-wide(>{_MAX_BASE_KEYS} keys)"
        return result, stats
    base = fetch_base_for_batch(table, period, result.rows, result.columns, compare)
    kept, skipped = split_unchanged_rows(result.rows, result.columns, base, compare, tol)
    stats["skipped"] = skipped
    stats["base_keys"] = len(base)
    if not kept:
        return None, stats
    return replace(result, rows=kept, rows_fetched=len(kept)), stats


def backfill_period(
    provider: InternalComputeProvider,
    period: str,
    start: str,
    end: str,
    dry_run: bool,
    skip_batches: int = 0,
    symbols_file: str | None = None,
    value_skip: bool = True,
) -> tuple[int, dict]:
    """单周期回填：provider.fetch → 值级跳过过滤 → BufferedWriter 批量写入。

    返回 (实际写入行数, 值级跳过度量 dict)。

    skip_batches: 跳过本周期前 N 批（断点续跑）。标的清单与 provider 同源
    （_get_symbols，ORDER BY symbol 序稳定），在生成器消费**前**切片——
    被跳过的标的完全不计算（旧版生成器消费后丢弃=白算 30 分钟实证）。
    ReplacingMergeTree 幂等，边界重叠无害。
    symbols_file: 显式标的清单文件（一行一个），优先级高于 skip_batches。
    value_skip: 关闭即回到"同键无条件重写"的旧行为（--no-value-skip，回滚位）。
    """
    payload = FetchPayload(
        table=TABLE,
        symbols=None,  # None → provider 自查 kline_{period} DISTINCT 标的
        start=datetime.date.fromisoformat(start),
        end=datetime.date.fromisoformat(end),
        incremental=False,
        extra={"period": period, "capability": "technical_indicator"},
    )
    if symbols_file:
        payload.symbols = [s.strip() for s in Path(symbols_file).read_text(encoding="utf-8").splitlines() if s.strip()]
        log.info("[%s] 使用标的清单 %d 个（%s）", period, len(payload.symbols), symbols_file)
    elif skip_batches > 0:
        all_symbols = provider._get_symbols(payload, period)
        cut = skip_batches * 100
        payload.symbols = list(all_symbols[cut:])
        log.info(
            "[%s] 断点续跑：跳过前 %d 批（%d 标的不计算），剩余 %d 个",
            period,
            skip_batches,
            min(cut, len(all_symbols)),
            len(payload.symbols),
        )

    numeric_all: frozenset[str] = frozenset()
    mode = "off"
    if not dry_run and value_skip:
        try:
            numeric_all = numeric_indicator_columns(TABLE)
            mode = "on"
        except Exception as e:  # noqa: BLE001 — 可比列都取不到时全程退回全量写，但必须响亮
            log.warning("[value-skip] 可比列现读失败 ⇒ 本次全程不跳写：%s", str(e)[:200])
            mode = "columns-error"
    metrics = {
        "period": period,
        "mode": mode,
        "tol": _VALUE_SKIP_REL_TOL,
        "batches": 0,
        "considered_rows": 0,
        "skipped_rows": 0,
        "written_rows": 0,
        "base_keys": 0,
        "degraded_batches": 0,
        "uncompared_value_columns": [],
    }

    writer = BufferedWriter(TABLE, max_seconds=30)
    total_rows = 0
    batch_idx = 0
    base_fail_streak = 0
    t0 = time.monotonic()
    log.info(
        "[%s] 回填开始 %s ~ %s（dry_run=%s，skip_batches=%d，value_skip=%s）",
        period,
        start,
        end,
        dry_run,
        skip_batches,
        mode,
    )
    for result in provider.fetch(payload, None):
        if result.error:
            log.error("[%s] FetchResult.error: %s", period, result.error)
            raise RuntimeError(f"[{period}] {result.error}")
        batch_idx += 1
        metrics["batches"] = batch_idx
        if not result.rows:
            continue
        if mode == "on":
            try:
                filtered, stats = value_skip_batch(result, period, numeric_all, TABLE)
                base_fail_streak = 0
            except Exception as e:  # noqa: BLE001 — 比对基失灵只准"少省"不准"少写"
                base_fail_streak += 1
                log.warning(
                    "[%s] 批 %d 比对基现读失败 ⇒ 本批全量写（连续第 %d 次）：%s",
                    period,
                    batch_idx,
                    base_fail_streak,
                    str(e)[:200],
                )
                if base_fail_streak >= _MAX_CONSECUTIVE_BASE_FAILURES:
                    # 熔断：本表 215 列的比对基读数在夜跑自身负载下会持续失败（2026-10-10 三形态
                    # 实测全灭），而每次失败要烧掉一整轮 TCP+HTTP 重试≈50s。不熔断＝把夜跑
                    # 从 21 分钟/片拖成几小时/片。停用是"少省"，不是"少写"，且 mode 进度量行可见。
                    mode = f"disabled-after-{base_fail_streak}-base-failures"
                    log.warning(
                        "[%s] 值级跳过熔断停用（连续 %d 次取不到比对基）⇒ 余下批次全量写，度量行 mode=%s 供账面判定",
                        period,
                        base_fail_streak,
                        mode,
                    )
                metrics["degraded_batches"] += 1
                filtered, stats = result, _neutral_stats(len(result.rows))
            metrics["considered_rows"] += stats["rows_in"]
            metrics["skipped_rows"] += stats["skipped"]
            metrics["base_keys"] += stats["base_keys"]
            if stats["degraded"] and mode == "on":
                metrics["degraded_batches"] += 1
            if stats["uncompared_columns"] and not metrics["uncompared_value_columns"]:
                metrics["uncompared_value_columns"] = stats["uncompared_columns"][:12]
            if filtered is None:
                continue
            result = filtered
        total_rows += len(result.rows)
        if not dry_run:
            if not writer.add(result):
                raise RuntimeError(f"[{period}] BufferedWriter.add 失败")
        if total_rows % 100_000 < len(result.rows):
            log.info("[%s] 累计 %d 行，耗时 %.0fs", period, total_rows, time.monotonic() - t0)
    if not dry_run:
        if not writer.flush():
            raise RuntimeError(f"[{period}] BufferedWriter.flush 失败")
    metrics["written_rows"] = total_rows
    metrics["mode"] = mode  # 熔断可能发生在中途，度量行必须报终态而不是开跑时的乐观态
    log.info(
        "[%s] 回填完成：写入 %d 行 / 参看 %d 行 / 跳过 %d 行 / 降级批 %d（mode=%s），耗时 %.0fs",
        period,
        total_rows,
        metrics["considered_rows"],
        metrics["skipped_rows"],
        metrics["degraded_batches"],
        mode,
        time.monotonic() - t0,
    )
    return total_rows, metrics


def main() -> int:
    ap = argparse.ArgumentParser(description="日/周/月技术指标历史回填（16号 §7⑥）")
    ap.add_argument("--periods", default="daily,weekly,monthly", help="逗号分隔周期（默认三周期）")
    ap.add_argument("--start-daily", default=_DEFAULT_STARTS["daily"])
    ap.add_argument("--start-weekly", default=_DEFAULT_STARTS["weekly"])
    ap.add_argument("--start-monthly", default=_DEFAULT_STARTS["monthly"])
    ap.add_argument("--end", default=datetime.date.today().isoformat())
    ap.add_argument(
        "--skip-daily-batches",
        type=int,
        default=0,
        help="daily 周期跳过前 N 批（断点续跑；与 provider 同源标的清单切片，被跳标的完全不计算）",
    )
    ap.add_argument(
        "--symbols-file",
        default=None,
        help="显式标的清单文件（一行一个 symbol），优先级高于 --skip-daily-batches",
    )
    ap.add_argument("--dry-run", action="store_true", help="只计算不写库")
    ap.add_argument(
        "--no-value-skip",
        action="store_true",
        help="关闭值级跳过（回到同键无条件重写的旧行为；回滚位，平时不该带）",
    )
    args = ap.parse_args()

    starts = {
        "daily": args.start_daily,
        "weekly": args.start_weekly,
        "monthly": args.start_monthly,
    }
    periods = [p.strip() for p in args.periods.split(",") if p.strip()]
    for p in periods:
        if p not in starts:
            ap.error(f"不支持周期: {p}（仅 daily/weekly/monthly）")

    provider = InternalComputeProvider()
    grand = 0
    all_metrics: list[dict] = []
    for p in periods:
        skip = args.skip_daily_batches if p == "daily" else 0
        rows, metrics = backfill_period(
            provider,
            p,
            starts[p],
            args.end,
            args.dry_run,
            skip_batches=skip,
            symbols_file=args.symbols_file,
            value_skip=not args.no_value_skip,
        )
        grand += rows
        all_metrics.append(metrics)
    # 机读标记行：分片编排器（tilib_dwm_shard_runner）从 stdout 末段抓这一行进片态，
    # 用 print 而非 log＝标记不能被日志格式/级别影响，且便于父进程逐行识别。
    for m in all_metrics:
        print(f"TI_VALUE_SKIP {json.dumps(m, ensure_ascii=False)}", flush=True)
    log.info("全部完成：%d 周期共 %d 行（幂等可重跑）", len(periods), grand)
    return 0


if __name__ == "__main__":
    sys.exit(main())
