# [BLUEPRINT] MOD-CHAINPILE-METAQ | 工单 WO-B3 §簇3-4（月度 30 条抽样：vintage 单调 + PIT 无未来函数）
# [MODULE] scripts.governance.meta_question.wo_b3_macro.audit_macro_vintage
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta_question.wo_b3_macro.macro_vintage;
#                 zephyr.infrastructure.database_service (reader); zephyr.data.ch_writer (sandbox 建/删)
# [CONSUMERS] 月度运维抽检（人工或后续登记为 reconciler 事件触发）；PQ-0185/PQ-0191 复考前置证据
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 抽样确定性：cityHash64(indicator_name, report_date) 升序取前 N（禁随机截断，保可复现）；
#              判据全机械（C1 版次连续/C2 存证一致/C3 零伪造/C4 PIT 无未来函数/C5 结构可存证）；
#              只读生产表——仅 --sandbox 在独立 selftest 表上跑多版通路（用毕即删，零触碰生产数据）；
#              历史 backfill_final 档 pub_ts 恒 NULL → C4 期望"取不到数"而非"取到回补终值"（宁缺勿假）。
# [MODIFY-GUARD] none
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 载表缺失->退出码 4 并提示先跑 apply_macro_vintage_ddl.py；任一判据不过->报告写盘+退出码 1。
# [TESTS] python scripts/governance/meta_question/wo_b3_macro/audit_macro_vintage.py --sandbox
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""宏观 vintage 存证月度抽检器（PQ-0185/PQ-0191 复考前置的运行账）。

用法::

    python .../audit_macro_vintage.py                        # 抽上一自然月 30 条
    python .../audit_macro_vintage.py --month 2026-08 --sample 30
    python .../audit_macro_vintage.py --sandbox              # 多版/PIT 通路自证（独立 selftest 表）
"""

from __future__ import annotations

import argparse
import calendar
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Final

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[3] / "src"))

import macro_vintage as mv  # noqa: E402

REPORT_DIR: Final = _HERE / "reports"
#: 闭卷切点（战役 PIT 边界）——PIT 抽样时点之一，用于证"切点前取不到未存证的回补值"
CUTOFF: Final = datetime.date(2025, 9, 9)
#: sandbox 表名派生自载表真源（mv.TABLE_VINTAGE ← TableRegistry 品类册，#ARCH-CH-024 Phase 5）
SANDBOX_TABLE: Final = f"{mv.TABLE_VINTAGE}_selftest"

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。mv.TABLE_VINTAGE / SANDBOX_TABLE 为模块常量、import 期
# 解析，落地文本与原内联表达式逐字等值；sample_keys 的动态日期/前缀/上限以语句头常量+调用处拼装保留。
_SQL_SAMPLE_PREFIX = f"SELECT indicator_name, report_date FROM {mv.TABLE_VINTAGE} "
_SQL_VINTAGE_SORTKEY = (
    f"SELECT sorting_key FROM system.tables WHERE database='c1_market' AND name='{mv.TABLE_VINTAGE.split('.')[1]}'"
)
_SQL_LEGACY_SORTKEY = "SELECT sorting_key FROM system.tables WHERE database='c1_market' AND name='macro_data'"
_SQL_COUNT_ROWS = f"SELECT count() FROM {mv.TABLE_VINTAGE}"
_SQL_COUNT_KEYS = f"SELECT uniqExact(indicator_name, report_date) FROM {mv.TABLE_VINTAGE}"
_SQL_BASIS_BREAKDOWN = f"SELECT pub_ts_basis, count() FROM {mv.TABLE_VINTAGE} GROUP BY pub_ts_basis ORDER BY 2 DESC"
_SQL_SANDBOX_STORED = f"SELECT vintage, pub_ts, indicator_value FROM {SANDBOX_TABLE} ORDER BY vintage"
_SQL_PROBE_TABLE = f"SELECT count() FROM {mv.TABLE_VINTAGE} LIMIT 1"


def _read(sql: str) -> list[tuple]:
    from zephyr.infrastructure.database_service import DatabaseService

    reader = DatabaseService().get_clickhouse_conn(role="reader")
    try:
        return list(reader.execute(sql))
    finally:
        reader.disconnect()


def _prev_month(today: datetime.date) -> str:
    first = today.replace(day=1)
    last = first - datetime.timedelta(days=1)
    return f"{last.year:04d}-{last.month:02d}"


def _month_window(month: str) -> tuple[datetime.date, datetime.date]:
    y, m = (int(x) for x in month.split("-"))
    return datetime.date(y, m, 1), datetime.date(y, m, calendar.monthrange(y, m)[1])


def sample_keys(month: str, size: int) -> list[tuple[str, datetime.date]]:
    """月窗内确定性抽样（哈希序，禁随机）；FRED_/EIA_ 各占一半（不足则互借）。"""
    start, end = _month_window(month)
    per = max(size // 2, 1)
    picked: list[tuple[str, datetime.date]] = []
    for prefix in ("FRED_", "EIA_"):
        rows = _read(
            _SQL_SAMPLE_PREFIX + f"WHERE report_date BETWEEN '{start}' AND '{end}' AND indicator_name LIKE '{prefix}%' "
            f"GROUP BY indicator_name, report_date ORDER BY cityHash64(indicator_name, toString(report_date)) "
            f"LIMIT {per}"
        )
        picked += [(str(n), d) for n, d in rows]
    if len(picked) < size:
        rows = _read(
            _SQL_SAMPLE_PREFIX + f"WHERE report_date BETWEEN '{start}' AND '{end}' "
            f"GROUP BY indicator_name, report_date "
            f"ORDER BY cityHash64(indicator_name, toString(report_date)) LIMIT {size}"
        )
        seen = set(picked)
        picked += [(str(n), d) for n, d in rows if (str(n), d) not in seen][: size - len(picked)]
    return picked[:size]


def fetch_versions(keys: list[tuple[str, datetime.date]]) -> list[tuple]:
    if not keys:
        return []
    pairs = ", ".join(f"('{n}','{d}')" for n, d in keys)
    return _read(
        f"SELECT indicator_name, report_date, vintage, pub_ts, pub_ts_basis, first_seen_ts, ingest_ts, "
        f"indicator_value FROM {mv.TABLE_VINTAGE} WHERE (indicator_name, report_date) IN ({pairs}) "
        f"ORDER BY indicator_name, report_date, vintage"
    )


def check_c1_versions(rows: list[tuple]) -> dict[str, Any]:
    """版次连续：同键 vintage 集 = 1..max，无缺号无重复。"""
    grouped: dict[tuple[str, str], list[int]] = {}
    for r in rows:
        grouped.setdefault((str(r[0]), str(r[1])), []).append(int(r[2]))
    bad = {f"{k[0]}|{k[1]}": sorted(v) for k, v in grouped.items() if sorted(v) != list(range(1, max(v) + 1))}
    multi = sum(1 for v in grouped.values() if max(v) > 1)
    return {
        "keys": len(grouped),
        "multi_vintage_keys": multi,
        "monotonic_no_gap": not bad,
        "violations": dict(list(bad.items())[:10]),
        "ok": not bad,
    }


def check_c2_evidence(rows: list[tuple]) -> dict[str, Any]:
    """存证一致性：按 basis 校 pub_ts 与观测时戳的关系（可复核，无一条越界才算过）。"""
    bad: list[str] = []
    by_basis: dict[str, int] = {}
    for name, rdate, vintage, pub_ts, basis, first_seen, ingest_ts, _v in rows:
        key = f"{name}|{rdate}|v{vintage}"
        by_basis[str(basis)] = by_basis.get(str(basis), 0) + 1
        if basis == mv._BASIS_OBSERVED and pub_ts is not None and pub_ts != first_seen:  # noqa: SLF001
            bad.append(f"{key}: ingest_observed 但 pub_ts≠first_seen_ts")
        if basis == mv._BASIS_OFFICIAL and pub_ts is not None and first_seen is not None and pub_ts > first_seen:  # noqa: E501, SLF001
            bad.append(f"{key}: official_release 发布晚于本仓首见（时戳依据存疑）")
        if pub_ts is not None and ingest_ts is not None and pub_ts > ingest_ts:
            bad.append(f"{key}: pub_ts 晚于落库时戳")
    return {"rows": len(rows), "by_basis": by_basis, "ok": not bad, "violations": bad[:10]}


def check_c3_no_fabrication(rows: list[tuple]) -> dict[str, Any]:
    """零伪造：backfill_final ⇒ pub_ts IS NULL；非 backfill ⇒ pub_ts 非空。"""
    bad_backfill = sum(1 for r in rows if r[4] == mv._BASIS_BACKFILL and r[3] is not None)  # noqa: SLF001
    bad_empty = sum(1 for r in rows if r[4] != mv._BASIS_BACKFILL and r[3] is None)  # noqa: SLF001
    return {
        "backfill_rows_with_pub_ts": bad_backfill,
        "non_backfill_rows_without_pub_ts": bad_empty,
        "ok": bad_backfill == 0 and bad_empty == 0,
    }


def check_c4_pit(keys: list[tuple[str, datetime.date]], month: str) -> dict[str, Any]:
    """PIT 无未来函数：SQL 模板 vs Python 暴力重算逐 as_of 一致，且返回行 pub_ts 必 ≤ as_of。"""
    start, end = _month_window(month)
    as_ofs = sorted(
        {
            datetime.datetime.combine(end, datetime.time.min, tzinfo=datetime.UTC),
            datetime.datetime.combine(start, datetime.time.min, tzinfo=datetime.UTC) - datetime.timedelta(days=30),
            datetime.datetime.combine(CUTOFF, datetime.time.min, tzinfo=datetime.UTC),
        }
    )
    names = ", ".join("'" + n.replace("'", "''") + "'" for n, _ in keys) or "''"
    mismatches: list[str] = []
    future_hits = 0
    returned = 0
    for as_of in as_ofs:
        stamp = as_of.strftime("%Y-%m-%d %H:%M:%S")
        sql = mv.PIT_LATEST_SQL.format(as_of=stamp, names_clause=f" AND indicator_name IN ({names})")
        api_rows = {(str(r[0]), str(r[1])): (round(float(r[2]), 4), r[3]) for r in _read(sql)}
        brute = {k: (round(float(v), 4), p) for k, (v, p) in _brute_pit(keys, as_of).items()}
        returned += len(api_rows)
        if api_rows != brute:
            mismatches.append(
                f"as_of={stamp} 与暴力重算不一致 api_only={sorted(set(api_rows) - set(brute))[:3]} "
                f"brute_only={sorted(set(brute) - set(api_rows))[:3]}"
            )
        future_hits += sum(1 for _k, (_v, pub) in api_rows.items() if pub is not None and pub > as_of)
    return {
        "as_of_points": [a.strftime("%Y-%m-%d") for a in as_ofs],
        "rows_returned_last_point": returned,
        "future_timestamp_rows": future_hits,
        "violations": mismatches[:5],
        "ok": future_hits == 0 and not mismatches,
        "note": "历史全为 backfill_final（pub_ts NULL）时 PIT 返回空=正确行为：宁缺勿假；"
        "非空返回须逐点等于暴力重算（本判据在 --sandbox 多版通路上亦跑）",
    }


def _brute_pit(
    keys: list[tuple[str, datetime.date]], as_of: datetime.datetime
) -> dict[tuple[str, str], tuple[float, Any]]:
    """暴力重算：直读原始行，取 pub_ts ≤ as_of 的 (pub_ts, vintage) 最大者。"""
    if not keys:
        return {}
    pairs = ", ".join(f"('{n}','{d}')" for n, d in keys)
    rows = _read(
        f"SELECT indicator_name, report_date, vintage, pub_ts, indicator_value "
        f"FROM {mv.TABLE_VINTAGE} WHERE (indicator_name, report_date) IN ({pairs})"
    )
    best: dict[tuple[str, str], tuple[Any, int, float]] = {}
    for name, rdate, vintage, pub_ts, value in rows:
        if pub_ts is None or pub_ts > as_of:
            continue
        key = (str(name), str(rdate))
        cand = (pub_ts, int(vintage), float(value))
        if key not in best or cand[:2] > best[key][:2]:
            best[key] = cand
    return {k: (v[2], v[0]) for k, v in best.items()}


def check_c5_structure() -> dict[str, Any]:
    from zephyr.data import ch_writer

    client = ch_writer.get_client_strict()
    try:
        vintage_key = str(client.execute(_SQL_VINTAGE_SORTKEY)[0][0])
        legacy_key = str(client.execute(_SQL_LEGACY_SORTKEY)[0][0])
    finally:
        client.disconnect()
    return {
        "vintage_sorting_key": vintage_key,
        "legacy_sorting_key": legacy_key,
        "ok": "vintage" in vintage_key and "vintage" not in legacy_key,
    }


def run_audit(month: str, sample: int) -> tuple[dict[str, Any], int]:
    keys = sample_keys(month, sample)
    rows = fetch_versions(keys)
    report: dict[str, Any] = {
        "carrier_table": mv.TABLE_VINTAGE,
        "month_window": month,
        "sampled_keys": len(keys),
        "sampled_rows": len(rows),
        "totals": {
            "rows": int(_read(_SQL_COUNT_ROWS)[0][0]),
            "keys": int(_read(_SQL_COUNT_KEYS)[0][0]),
            "by_basis": [list(r) for r in _read(_SQL_BASIS_BREAKDOWN)],
        },
        "C1_vintage_monotonic": check_c1_versions(rows),
        "C2_evidence_consistency": check_c2_evidence(rows),
        "C3_no_fabrication": check_c3_no_fabrication(rows),
        "C4_pit_no_lookahead": check_c4_pit(keys, month),
        "C5_structure": check_c5_structure(),
    }
    ok = all(
        report[k].get("ok", False)
        for k in (
            "C1_vintage_monotonic",
            "C2_evidence_consistency",
            "C3_no_fabrication",
            "C4_pit_no_lookahead",
            "C5_structure",
        )
    )
    report["verdict"] = "PASS" if ok else "FAIL"
    return report, 0 if ok else 1


# ------------------------------------------------------------------ sandbox 多版通路自证


def run_sandbox() -> dict[str, Any]:
    """在独立 selftest 表上跑"初值→修订→PIT 取数"全通路（生产表零写入，用毕即删）。"""
    from zephyr.data import ch_writer

    client = ch_writer.get_client_strict()
    out: dict[str, Any] = {}
    try:
        client.execute(f"DROP TABLE IF EXISTS {SANDBOX_TABLE}")
        client.execute(
            f"CREATE TABLE {SANDBOX_TABLE} AS {mv.TABLE_VINTAGE} "
            "ENGINE = ReplacingMergeTree(ingest_ts) PARTITION BY toYYYYMM(report_date) "
            "ORDER BY (indicator_name, report_date, vintage)"
        )
        day = datetime.date(2026, 8, 5)
        obs_v1 = datetime.datetime(2026, 8, 6, 2, 0, 0, tzinfo=datetime.UTC)
        obs_v2 = datetime.datetime(2026, 9, 6, 2, 0, 0, tzinfo=datetime.UTC)
        initial = [(day, "SBX_FRED_CPI", 318.0, "指数", "monthly", "fred")]
        r1, s1 = mv.resolve_vintages(initial, {}, source_series_id="SBX", observed_at=obs_v1)
        client.execute(mv.insert_sql(SANDBOX_TABLE), r1, types_check=False)
        existing = {("SBX_FRED_CPI", str(day)): {"max_vintage": 1, "values": [318.0]}}
        r2, s2 = mv.resolve_vintages(
            [(day, "SBX_FRED_CPI", 318.4, "指数", "monthly", "fred")],
            existing,
            source_series_id="SBX",
            observed_at=obs_v2,
        )
        client.execute(mv.insert_sql(SANDBOX_TABLE), r2, types_check=False)
        same = mv.resolve_vintages(
            [(day, "SBX_FRED_CPI", 318.4, "指数", "monthly", "fred")],
            {("SBX_FRED_CPI", str(day)): {"max_vintage": 2, "values": [318.0, 318.4]}},
            observed_at=obs_v2,
        )
        stored = client.execute(_SQL_SANDBOX_STORED)
        pit_before = client.execute(
            mv.PIT_LATEST_SQL.format(
                as_of="2026-08-31 00:00:00",
                names_clause=" AND indicator_name='SBX_FRED_CPI'",
            ).replace(mv.TABLE_VINTAGE, SANDBOX_TABLE)
        )
        pit_after = client.execute(
            mv.PIT_LATEST_SQL.format(
                as_of="2026-09-20 00:00:00",
                names_clause=" AND indicator_name='SBX_FRED_CPI'",
            ).replace(mv.TABLE_VINTAGE, SANDBOX_TABLE)
        )
        out = {
            "stats_v1": s1,
            "stats_v2": s2,
            "same_value_replay_skip": same[1]["unchanged_skip"],
            "stored_versions": [[int(v), str(p), float(x)] for v, p, x in stored],
            "pit_2026_08_31_returns_only_v1": [(int(v), float(x)) for _n, _d, x, _p, v, _b in pit_before],
            "pit_2026_09_20_returns_v2": [(int(v), float(x)) for _n, _d, x, _p, v, _b in pit_after],
            "ok": (
                [int(v) for v, _p, _x in stored] == [1, 2]
                and float(stored[0][2]) == 318.0
                and float(stored[1][2]) == 318.4
                and len(pit_before) == 1
                and int(pit_before[0][4]) == 1
                and int(pit_after[0][4]) == 2
                and same[1]["unchanged_skip"] == 1
            ),
        }
    finally:
        client.execute(f"DROP TABLE IF EXISTS {SANDBOX_TABLE}")
        client.disconnect()
    return out


def main(argv: list[str] | None = None) -> int:
    from zephyr.shared.utils.time_utils import now_utc

    parser = argparse.ArgumentParser(description="宏观 vintage 存证月度抽检")
    parser.add_argument("--month", default=None, help="抽样月窗 YYYY-MM（默认上一自然月）")
    parser.add_argument("--sample", type=int, default=30, help="抽样键数（默认 30，月度纪律）")
    parser.add_argument("--sandbox", action="store_true", help="多版/PIT 通路自证（独立 selftest 表）")
    args = parser.parse_args(argv)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if args.sandbox:
        res = run_sandbox()
        stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
        path = REPORT_DIR / f"vintage_sandbox_{stamp}.json"
        path.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        print(f"[sandbox] 报告={path} verdict={'PASS' if res.get('ok') else 'FAIL'}")
        return 0 if res.get("ok") else 1

    month = args.month or _prev_month(now_utc().date())
    try:
        _read(_SQL_PROBE_TABLE)
    except Exception as exc:  # noqa: BLE001 — 载体缺失要给出可执行指引，不做无意义堆栈
        print(f"[FAIL] 载表不可读（先跑 apply_macro_vintage_ddl.py）：{type(exc).__name__}: {str(exc)[:120]}")
        return 4
    report, code = run_audit(month, args.sample)
    path = REPORT_DIR / f"vintage_audit_{month.replace('-', '')}.yaml"
    import yaml

    path.write_text(
        yaml.safe_dump(report, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "totals"}, ensure_ascii=False, indent=1, default=str))
    print(f"[audit] 月窗={month} 抽样={report['sampled_keys']} 判定={report['verdict']} 报告={path}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
