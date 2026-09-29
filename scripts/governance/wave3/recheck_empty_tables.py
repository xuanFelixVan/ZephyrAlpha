#!/usr/bin/env python
# create-guard-not-dup: 本件是 W-180.3 空壳表 strict 复测器（M4 工单 C134 处方，MOD-GOV-wave3-empty-recheck），对在册空壳表清单走 ch_reader.count_strict 严格读通道复测并出具三态翻案报告，CREATE-GUARD 三条命中（now iso/check ident）均为子串误命中，非 session_required_gate/shrinkage_backtest_engine/ops_guard_delete_interception 的第二真源
# [TTL] task_bound
# [MODULE] scripts.governance.wave3.recheck_empty_tables | module_id=MOD-GOV-wave3-empty-recheck | layer=script | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.0/3.5（W-180.3 strict 复测 + Z-17 三分补登记）
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(argparse/json/time/datetime/pathlib/dataclasses/re)；yaml；zephyr.data.ch_reader.count_strict/query_rows（严格读通道，唯一读数层）；zephyr.data.ch_writer.last_transport
# [CONSUMERS] docs/_working/total_command_closeout/wave3/empty_tables_recheck.md（案卷）；src/zephyr/data/config/known_data_gaps.yaml（--apply-gaps 纯追加）
# [STARTUP] on_demand: 施工队命令行一次性复测，无常驻调度
# [MATURITY] draft
# [INVARIANTS] 只读取证（禁 DDL/DML）；三态必分——"读失败"永不并入"真空"；计数以 strict 现读为准禁照抄旧数（9/10/11 皆旧口径）；known_data_gaps 只纯追加，删除集必为空
# [MODIFY-GUARD] 改判据口径（三态阈值/表清单）须与案卷 empty_tables_recheck.md 及 92 册验收尺同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 传输/引擎/形状异常 -> 该表记 verdict=read_failed 并保留异常原文（禁降级为 0/真空）；gap 追加不变量断言失败 -> 抛 GapAppendInvariantError 且不落盘
# [TESTS] 本件即一次性普查件：产物 TSV/JSON 与案卷读数同批可复算；不变量断言（键集合差＋逐条深比对）内置于 --apply-gaps 路径
"""W-34 空壳表 strict 复测器（波 3.0/3.5）——把"查询失败"从"表是空的"里摘出来。

大白话：`ch_reader.count()` 出错时**返回 0**（`src/zephyr/data/ch_reader.py:131` 契约原文
"查询失败返回 0"），所以 W-34 那份"9–10 张空壳表"里，可能混着"根本没读到"的假空壳。
本件对在册点名的每张表走 **strict 通道**（`count_strict()` 失败必抛、真 0 行才是确证空表），
逐表输出：表名／strict 行数／传输路径（tcp:9000 或 http:8123）／耗时／UTC 时间戳／三态判定。

三态（互斥，"读失败"单列）：
  vacuum_confirmed  count_strict 确证 0 行且表在 system.tables 带库限在册
  has_data          count_strict > 0（旧清单若判其空壳 ⇒ 假空壳，须翻案）
  read_failed       CH 不可达／传输全败／形状异常／表不在册（子因单列，绝不当"真空"证据）

内收（§4 全资产净零）：本件**不实现第二套读数层**，只做普查编排＋分箱＋补登记，
严格读面复用 `zephyr.data.ch_reader.count_strict/query_rows`（W-180.1）与
`scripts/governance/data_supply/ch_probe.py` 的记录字段口径；仓内既有普查件
（`scripts/governance/data_supply/`）零复制、零阈值新增、零 gate 新增。

用法：
    PYTHONPATH=<lane>/src python scripts/governance/wave3/recheck_empty_tables.py \
        --out-tsv docs/_working/total_command_closeout/wave3/empty_tables_recheck.tsv \
        --out-json docs/_working/total_command_closeout/wave3/empty_tables_recheck.yaml
    ... --apply-gaps            # 仅对 vacuum_confirmed 且未登记者纯追加 known_data_gaps.yaml
    ... --dry-run-gaps          # 只打印将要追加的条目，不写盘
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

GAPS_YAML = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "known_data_gaps.yaml"

#: 三态判定常量（禁增第四态；"表不存在"是 read_failed 的子因，不是真空）
VACUUM_CONFIRMED = "vacuum_confirmed"
HAS_DATA = "has_data"
READ_FAILED = "read_failed"

#: 曾被判为"空壳"的表全集——**现读复原**自在册件（非记忆、非旧清单照抄）：
#:   · docs/_working/chain_fullflow_closeout/business_pipeline_skeleton.md:147-152（病灶 B：已知 4 张 + 扩面 10 张）
#:   · docs/_working/chain_fullflow_closeout/mine_pipe_blockage_substages.md:121（"9 张"但点名 8 张）
#:   · docs/_working/total_command_closeout/dossier_G_business_chain.md:116-141（实读面 12 张，suspend 非 0）
#: 并集去重＝下列 14 张；未登记的 gap 追加只走 strict 确证真空者。
CENSUS_TABLES: tuple[str, ...] = (
    "c1_market.suspend",
    "c1_market.account_nav_daily",
    "c1_market.etf_benchmark",
    "c1_market.l2_tick",
    "c1_market.edb_data",
    "c1_market.realtime_snapshot",
    "c1_market.index_valuation_daily_v2",
    "c1_market.ipo_schedule",
    "c1_market.margin_target_adjustment",
    "c1_market.market_index_meta",
    "c1_market.msci_adjustment",
    "c1_market.reconciliation_differences",
    "c1_market.stock_candidate_pool",
    "c1_market.stock_valuation",
)

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")

#: 判据类 SQL 集中化（§5.160.2 NO-BARE-SQL）：模板置模块级常量，调用方仅填经 `_check_ident` 白名单的标识符。
SQL_TABLE_EXISTS_TMPL = "SELECT count() AS n FROM system.tables WHERE database='{db}' AND name='{tb}'"
SQL_CENSUS_SENTINEL_TMPL = "SELECT count() AS n FROM system.tables WHERE database='{db}'"
SQL_FIRST_DATE_COL_TMPL = (
    "SELECT name FROM system.columns WHERE database='{db}' AND table='{tb}'"
    " AND (type LIKE 'Date%' OR type LIKE 'DateTime%') ORDER BY position LIMIT 1"
)
#: 证据用计数语句（实际执行由 `ch_reader.count_strict` 构造并按引擎探测注入 FINAL）
SQL_COUNT_TMPL = "SELECT count() FROM {table} FINAL"


class GapAppendInvariantError(RuntimeError):
    """known_data_gaps 追加后不变量不成立（条目被删/被改）——硬抛，不落盘。"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class EmptyTableRecheckRow:
    """One strict-channel recheck record for one table (machine-readable row)."""

    table: str
    strict_rows: int | None
    transport: str
    elapsed_ms: float
    ts_utc: str
    verdict: str
    sub_cause: str = ""
    table_in_system_tables: bool | None = None
    sql_count: str = ""
    error_detail: str = ""
    old_claim: str = ""


@dataclass
class RecheckReport:
    rows: list[EmptyTableRecheckRow] = field(default_factory=list)
    ch_reachable: bool | None = None
    probe_ts_utc: str = ""
    counts: dict[str, int] = field(default_factory=dict)


def _check_ident(name: str) -> str:
    if not _IDENT.match(name or ""):
        raise ValueError(f"表名非法（禁裸 SQL 注入面）: {name!r}")
    return name


def _transport_label(ch_writer: Any) -> str:
    """最近一次严格读实际成功的传输路径 → 'tcp:9000' / 'http:8123' / 'unknown'。"""
    kind = (ch_writer.last_transport() or "").strip().lower()
    if kind == "tcp":
        return f"tcp:{getattr(ch_writer, '_CH_TCP_PORT', 9000)}"
    if kind == "http":
        return f"http:{getattr(ch_writer, '_CH_HTTP_PORT', 8123)}"
    return "unknown"


def probe_connectivity(ch_reader: Any) -> tuple[bool, str, str]:
    """CH 可达性哨兵（带库限，防 N6"跨库探测静默返回 0"坑）。"""
    t0 = time.perf_counter()
    try:
        rows = ch_reader.query_rows(SQL_CENSUS_SENTINEL_TMPL.format(db="c1_market"), timeout=15)
        n = int(str(rows[0][0]).strip()) if rows and rows[0] else -1
        el = (time.perf_counter() - t0) * 1000
        if n < 0:
            return False, f"哨兵返回形状异常 rows={rows!r}", "unknown"
        return True, f"c1_market 在册表数={n}（elapsed {el:.0f}ms）", ""
    except Exception as exc:  # noqa: BLE001  可达性探测失败必如实报，禁降级
        return False, f"{type(exc).__name__}: {exc}", "unknown"


def table_in_system_tables(ch_reader: Any, database: str, name: str) -> bool:
    """带 `database=` 库限的在册探测（dossier_G N6：跨库 LIKE 会静默 0，必须限库）。"""
    _check_ident(f"{database}.{name}")
    sql = SQL_TABLE_EXISTS_TMPL.format(db=database, tb=name)
    rows = ch_reader.query_rows(sql, timeout=20)
    if not rows or len(rows[0]) != 1:
        raise RuntimeError(f"system.tables 探测形状异常: {rows!r}")
    return int(str(rows[0][0]).strip()) > 0


def detect_date_column(ch_reader: Any, database: str, name: str) -> str:
    """gap 条目 date_column 现读：取首个 Date/DateTime 列；无则空串（照既有 "" 先例）。"""
    _check_ident(f"{database}.{name}")
    sql = SQL_FIRST_DATE_COL_TMPL.format(db=database, tb=name)
    rows = ch_reader.query_rows(sql, timeout=20)
    if not rows:
        return ""
    return str(rows[0][0])


def recheck_table(
    ch_reader: Any,
    ch_writer: Any,
    table: str,
    old_claim: str,
    elapsed_hook: Callable[[], float] | None = None,
) -> EmptyTableRecheckRow:
    """单表 strict 复测：任何异常都归 read_failed，**永不**洗成 vacuum_confirmed。"""
    db, _, name = table.partition(".")
    sql_count = SQL_COUNT_TMPL.format(table=table)
    t0 = time.perf_counter()
    try:
        exists = table_in_system_tables(ch_reader, db, name)
        if not exists:
            return EmptyTableRecheckRow(
                table=table,
                strict_rows=None,
                transport=_transport_label(ch_writer),
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                ts_utc=_now_iso(),
                verdict=READ_FAILED,
                sub_cause="table_missing_in_ch",
                table_in_system_tables=False,
                sql_count=sql_count,
                error_detail=f"{db} 库内无表 {name}（带库限 system.tables 实读）",
                old_claim=old_claim,
            )
        n = ch_reader.count_strict(table, timeout=30)
        return EmptyTableRecheckRow(
            table=table,
            strict_rows=n,
            transport=_transport_label(ch_writer),
            elapsed_ms=(time.perf_counter() - t0) * 1000,
            ts_utc=_now_iso(),
            verdict=VACUUM_CONFIRMED if n == 0 else HAS_DATA,
            sub_cause="",
            table_in_system_tables=True,
            sql_count=sql_count,
            old_claim=old_claim,
        )
    except Exception as exc:  # noqa: BLE001  W-180.1：失败态必须单列并留原文
        return EmptyTableRecheckRow(
            table=table,
            strict_rows=None,
            transport=_transport_label(ch_writer),
            elapsed_ms=(time.perf_counter() - t0) * 1000,
            ts_utc=_now_iso(),
            verdict=READ_FAILED,
            sub_cause="strict_read_error",
            sql_count=sql_count,
            error_detail=f"{type(exc).__name__}: {exc}"[:600],
            old_claim=old_claim,
        )


def run_census(tables: tuple[str, ...] | list[str]) -> RecheckReport:
    from zephyr.data import ch_reader, ch_writer  # 严格读通道唯一入口（禁 query()/count()）

    report = RecheckReport(probe_ts_utc=_now_iso())
    ok, detail, _ = probe_connectivity(ch_reader)
    report.ch_reachable = ok
    if not ok:
        for t in tables:
            report.rows.append(
                EmptyTableRecheckRow(
                    table=t,
                    strict_rows=None,
                    transport="unknown",
                    elapsed_ms=0.0,
                    ts_utc=_now_iso(),
                    verdict=READ_FAILED,
                    sub_cause="ch_unreachable",
                    sql_count=SQL_COUNT_TMPL.format(table=t),
                    error_detail=f"CH 不可达/哨兵失败: {detail}",
                )
            )
    else:
        for t in tables:
            report.rows.append(recheck_table(ch_reader, ch_writer, t, "在册旧判=空壳（count() 通道）"))
    for r in report.rows:
        report.counts[r.verdict] = report.counts.get(r.verdict, 0) + 1
    return report


# ---------------------------------------------------------------- known_data_gaps 纯追加


def load_gaps(text: str) -> list[dict[str, Any]]:
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict) or not isinstance(doc.get("gaps"), list):
        raise GapAppendInvariantError("known_data_gaps.yaml 解析失败或无 gaps 列表——禁追加")
    return doc["gaps"]


def registered_tables(entries: list[dict[str, Any]]) -> set[str]:
    return {str(e.get("table") or "") for e in entries}


def registered_ids(entries: list[dict[str, Any]]) -> set[str]:
    return {str(e.get("id") or "") for e in entries}


def build_gap_entry(
    row: EmptyTableRecheckRow,
    date_column: str,
    today: str,
) -> dict[str, Any]:
    """照既有 empty_table 条目字段顺序生成（不自创字段名）。"""
    plain = row.table.split(".", 1)[1]
    return {
        "id": f"{plain}_strict_recheck_empty",
        "table": row.table,
        "gap_type": "empty_table",
        "start_date": "",
        "end_date": "",
        "date_column": date_column,
        "detection_threshold": 1,
        "status": "open",
        "root_cause": (
            f"波 3.0 strict 复测（{row.ts_utc}，传输通道 {row.transport}，count_strict 确证 0 行）："
            "该表在册且 0 行，缺「建采集腿 vs 退役」的处置；本次仅登记缺，不代 Owner 裁定。"
        ),
        "impact": f"c1_market 表 {plain} 无数据可读；W-34 旧清单曾以 count()（失败返回 0）通道判其空壳。",
        "evidence": (
            f"scripts/governance/wave3/recheck_empty_tables.py --out-json；SQL={row.sql_count}；"
            f"strict_rows={row.strict_rows}；elapsed={row.elapsed_ms:.1f}ms；"
            f"案卷=docs/_working/total_command_closeout/wave3/empty_tables_recheck.md"
        ),
        "resolution_plan": (
            "待处置两选一：①为该产品域建采集腿（tasks.yaml + provider 接线）；"
            "②按 #311/#328 条件通道隔离退役（rename 隔离 7 天再 DROP，三层调查留证）。"
            "本班不改判据、不执行 DDL。"
        ),
        "created": today,
        "last_updated": today,
    }


def render_gap_block(entry: dict[str, Any]) -> str:
    """YAML 块渲染：字段顺序与既有条目一致，2 空格缩进 + `  - id:` 起头。"""
    lines = [f"  - id: {_q(entry['id'])}"]
    for key in ("table", "gap_type", "start_date", "end_date", "date_column"):
        val = entry.get(key)
        lines.append(f"    {key}: {_q(val if val is not None else '')}")
    lines.append(f"    detection_threshold: {entry['detection_threshold']}")
    lines.append(f"    status: {_q(entry['status'])}")
    for key in ("root_cause", "impact", "evidence", "resolution_plan", "created", "last_updated"):
        lines.append(f"    {key}: {_q(entry[key])}")
    return "\n".join(lines) + "\n"


def _q(value: Any) -> str:
    text = "" if value is None else str(value)
    return json.dumps(text, ensure_ascii=False)


def _verify_append_invariants(
    before: list[dict[str, Any]], before_ids: set[str], new_text: str, to_add: list[dict[str, Any]]
) -> None:
    """写盘前不变量断言（纯追加三证）：删除集为空、条目数足增、既有条目零改动、文本零 CRLF。"""
    after = load_gaps(new_text)
    after_ids = registered_ids(after)
    deletion = before_ids - after_ids
    if deletion:
        raise GapAppendInvariantError(f"不变量违背：既有 gap id 删除集非空 {sorted(deletion)}")
    if len(after) < len(before) + len(to_add):
        raise GapAppendInvariantError(f"不变量违背：条目数 {len(before)}→{len(after)}，少于应增 {len(to_add)}")
    by_id = {str(e.get("id")): e for e in after}
    mutated = [gid for gid, g in ((str(x.get("id")), x) for x in before) if by_id.get(gid) != g]
    if mutated:
        raise GapAppendInvariantError(f"不变量违背：既有 gap 条目被改动 {mutated}")
    if new_text.count("\r\n") or "\r\n" in new_text:
        raise GapAppendInvariantError("不变量违背：写盘文本含 CRLF，须 newline='\\n'")


def append_gaps(entries: list[dict[str, Any]], gaps_path: Path = GAPS_YAML) -> dict[str, Any]:
    """纯追加：只在 gaps 列表尾部插入新条目，既有文本零改动；写前后各做一次解析+不变量断言。"""
    original = gaps_path.read_text(encoding="utf-8")
    before = load_gaps(original)
    before_ids, before_tables = registered_ids(before), registered_tables(before)
    for e in before:
        if not str(e.get("id") or ""):
            raise GapAppendInvariantError("既有 gap 条目缺 id——无法做键集合差断言，中止")

    already = {str(e["table"]) for e in entries} & before_tables
    to_add = [e for e in entries if e["table"] not in before_tables and e["id"] not in before_ids]
    dup_ids = [e["id"] for e in to_add if e["id"] in before_ids]
    if dup_ids:
        raise GapAppendInvariantError(f"新 gap id 与既有冲突: {dup_ids}")

    insert_at = _gap_list_tail_offset(original)
    block = "\n  # === 2026-09-27 波 3.0 W-34 strict 复测补登记（recheck_empty_tables.py 机生，勿手改）===\n"
    block += "".join(render_gap_block(e) + "\n" for e in to_add)
    new_text = original[:insert_at] + block + original[insert_at:]

    _verify_append_invariants(before, before_ids, new_text, to_add)

    if to_add:
        with open(gaps_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new_text)
    verify = load_gaps(gaps_path.read_text(encoding="utf-8"))
    return {
        "before_count": len(before),
        "after_count": len(verify),
        "added_ids": [e["id"] for e in to_add],
        "skipped_already_registered": sorted(already),
        "deletion_set": sorted(before_ids - registered_ids(verify)),
        "mutated_existing": [
            gid
            for gid, g in ((str(x.get("id")), x) for x in before)
            if {str(e.get("id")): e for e in verify}.get(gid) != g
        ],
    }


def _gap_list_tail_offset(text: str) -> int:
    """返回"gaps 列表最后一个条目之后、任何顶层键之前"的插入点（保证纯追加不破 YAML 结构）。"""
    lines = text.split("\n")
    last_content = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1] not in (" ", "\t"):
            if idx == 0 or stripped.startswith("gaps:"):
                continue
            # 顶层键（如文件尾的 last_updated:）——列表到此为止
            return sum(len(lines[i]) + 1 for i in range(idx))
        last_content = idx
    return len(text) if last_content is None else sum(len(lines[i]) + 1 for i in range(last_content + 1))


# ---------------------------------------------------------------- 输出


def write_outputs(report: RecheckReport, tsv: Path, js: Path) -> None:
    cols = [
        "table",
        "verdict",
        "strict_rows",
        "transport",
        "elapsed_ms",
        "ts_utc",
        "sub_cause",
        "table_in_system_tables",
        "sql_count",
        "old_claim",
        "error_detail",
    ]
    tsv.parent.mkdir(parents=True, exist_ok=True)
    with open(tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in report.rows:
            d = asdict(r)
            fh.write("\t".join(str(d[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    js.write_text(
        json.dumps(
            {
                "probe_ts_utc": report.probe_ts_utc,
                "ch_reachable": report.ch_reachable,
                "counts": report.counts,
                "rows": [asdict(r) for r in report.rows],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
        newline="\n",
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="W-34 空壳表 strict 复测（波 3.0/3.5）")
    ap.add_argument("--out-tsv", default=".runtime/tmp/wave3_empty_tables/empty_tables_recheck.tsv")
    ap.add_argument("--out-json", default=".runtime/tmp/wave3_empty_tables/empty_tables_recheck.json")
    ap.add_argument("--apply-gaps", action="store_true", help="对确证真空且未登记者纯追加 known_data_gaps.yaml")
    ap.add_argument("--dry-run-gaps", action="store_true", help="只打印将追加的条目")
    ap.add_argument("--gaps-path", default=str(GAPS_YAML))
    args = ap.parse_args(argv)

    report = run_census(CENSUS_TABLES)
    write_outputs(
        report,
        (_REPO_ROOT / args.out_tsv) if not Path(args.out_tsv).is_absolute() else Path(args.out_tsv),
        (_REPO_ROOT / args.out_json) if not Path(args.out_json).is_absolute() else Path(args.out_json),
    )
    print(f"[INFO] ch_reachable={report.ch_reachable} counts={report.counts} ts={report.probe_ts_utc}")
    for r in report.rows:
        print(
            f"[ROW] {r.table}\t{r.verdict}\trows={r.strict_rows}\ttransport={r.transport}\t"
            f"elapsed={r.elapsed_ms:.1f}ms\t{r.sub_cause}{(':: ' + r.error_detail) if r.error_detail else ''}"
        )

    if args.apply_gaps or args.dry_run_gaps:
        from zephyr.data import ch_reader  # date_column 现读也走严格通道

        candidates = [r for r in report.rows if r.verdict == VACUUM_CONFIRMED]
        entries = []
        today = datetime.now(timezone.utc).date().isoformat()
        for r in candidates:
            db, _, name = r.table.partition(".")
            try:
                dc = detect_date_column(ch_reader, db, name)
            except Exception as exc:  # noqa: BLE001
                dc = ""
                r.error_detail += f" | date_column 探测失败: {type(exc).__name__}: {exc}"
            entries.append(build_gap_entry(r, dc, today))
        if args.dry_run_gaps:
            print("[DRY] 将追加条目：")
            for e in entries:
                print(render_gap_block(e))
            print(f"[DRY] 候选 {len(entries)} 条（仅 vacuum_confirmed；read_failed 永不追加）")
            return 0
        result = append_gaps(entries, Path(args.gaps_path))
        print("[GAPS] " + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
