#!/usr/bin/env python
# [TTL] task_bound
# [STARTUP] on_demand: 人工/施工队/审计员命令行调用（python scripts/governance/data_supply/ch_probe.py --sql "..."），无常驻调度
# [CONSUMERS] docs/_working/total_command_closeout/wave1a/dead_store_triage.md §5（W-34 复测配方）; 波 3 空壳表复测; 任何判据类 CH 读数; W-180 落地批 st-nightsweep-sw4-20260929（aidrafts st-final-build-20260926 移植；卡面指定 scripts/data/ 系 gitignore 路径(.gitignore:604 scripts/data/*)无法入库，按 aidrafts 原位落 scripts/governance/data_supply/）
# [MODULE] module_id=MOD-GOV-wave1a-ch_probe | layer=script | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/subprocess/json/re/datetime)；yaml
# [MATURITY] draft
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# create-guard-not-dup: 数据供给侧 CH 探针（JSON 序列化金丝雀测试靶件，tests/governance/test_ch_probe_json_serialization_canary 专用）；与 ops/ch_health_probe（存活探测）及 drift brain 集成件职责不同源
"""CH 读数标准探针（W-180.4）——把 X-26 立法的"双探测/证据降级"工具化。

大白话：以前每个人每条判据读数都手写一遍探测，结果审计员自己把 TSV 字符串按字符
劈开、把"查询失败"读成"表是空的"。本探针一次调用输出一行 JSONL，把
**查询原文 / 实际执行 SQL（FINAL 注入后）/ 传输路径 / 耗时 / 行数 / 首行样本 / 时间戳**
全记下来；失败**显式报红**（退出码非 0 + `[RED]` 行），绝不静默降级成空表。

红线（W-180 追加）：判据类读数必须走 `query_rows` / `count_strict` / 本探针 三选一。

用法：
    python scripts/governance/data_supply/ch_probe.py --sql "SELECT count() FROM system.tables WHERE database='c1_market'"
    python scripts/governance/data_supply/ch_probe.py --count c1_market.kline_daily
    python scripts/governance/data_supply/ch_probe.py --count-sql c1_market.kline_daily --where "dt >= '2026-01-01'"
    python scripts/governance/data_supply/ch_probe.py --file my_probes.sql      # 每行一条 SQL（# 开头为注释）
    ... --out-dir .runtime/tmp/ch_probe --json                # 产物落 TTL 暂存区
"""

from __future__ import annotations

import argparse
import datetime
import decimal
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = (
    Path(__file__).resolve().parents[3]
)  # scripts/governance/data_supply/ → 仓根（原 aidrafts 件 parents[2]=scripts/ 系深度病：产物误落 scripts/.runtime、src 注入失效，2026-09-29 SW4 修正）
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.data import ch_reader, ch_writer  # noqa: E402  （探针本体即严格通道的首个消费者）


def _now_iso() -> str:
    """_now_iso implementation."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _blank_rec(channel: str) -> dict:
    """_blank_rec implementation."""
    return {
        "ts_utc": _now_iso(),
        "sql_raw": None,
        "sql_executed": None,
        "transport": None,
        "elapsed_ms": None,
        "rows": None,
        "first_row_sample": None,
        "outcome": "fail",
        "error": None,
        "channel": channel,
    }


def probe_sql(sql: str, timeout: int) -> dict:
    """跑一条只读 SQL，返回机读记录（outcome ∈ ok / empty / fail）。"""
    rec = _blank_rec("ch_reader.query_rows(strict)")
    rec["sql_raw"] = sql
    t0 = time.monotonic()
    try:
        executed = ch_reader.inject_final_strict(sql)
        rec["sql_executed"] = executed
        rows = ch_writer.query_strict(executed, timeout=timeout)
    except ch_writer.ClickHouseQueryError as e:
        rec["elapsed_ms"] = round((time.monotonic() - t0) * 1000, 1)
        rec["transport"] = ch_writer.last_transport() or "none"
        rec["error"] = {"type": type(e).__name__, "attempts": [list(a) for a in e.attempts]}
        return rec
    rec["elapsed_ms"] = round((time.monotonic() - t0) * 1000, 1)
    rec["transport"] = ch_writer.last_transport() or "unknown"
    rec["rows"] = len(rows)
    rec["first_row_sample"] = list(rows[0]) if rows else None
    rec["outcome"] = "ok" if rows else "empty"
    return rec


def probe_count(table: str, where: str, timeout: int) -> dict:
    """表计数（count_strict：失败必抛，"真 0 行"与"查询失败"两态可分）。"""
    rec = _blank_rec("ch_reader.count_strict(strict)")
    rec["sql_raw"] = f"<count {table} where={where!r}>"
    t0 = time.monotonic()
    try:
        final = ch_reader._final_suffix_strict(table)  # noqa: SLF001 — 探针须报告实际执行 SQL
    except ch_writer.ClickHouseQueryError as e:
        rec.update(
            {
                "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                "transport": "none",
                "error": {"type": type(e).__name__, "attempts": [list(a) for a in e.attempts]},
            }
        )
        return rec
    sql = ch_reader._SQL_COUNT.format(table=table, final=final)  # noqa: SLF001 — 复述实际执行口径，禁另立模板
    if where:
        sql += f" WHERE {where}"
    rec["sql_executed"] = sql
    t0 = time.monotonic()
    try:
        n = ch_reader.count_strict(table, where=where, timeout=timeout)
    except ch_writer.ClickHouseQueryError as e:
        rec.update(
            {
                "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                "transport": ch_writer.last_transport() or "none",
                "error": {"type": type(e).__name__, "attempts": [list(a) for a in e.attempts]},
            }
        )
        return rec
    rec.update(
        {
            "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
            "transport": ch_writer.last_transport() or "unknown",
            "rows": 1,
            "first_row_sample": [n],
            "count": n,
            "outcome": "ok" if n > 0 else "empty",
        }
    )
    return rec


def _jsonable(v: object) -> str:
    """探针落盘的兜底序列化：Date/Datetime/Decimal/UUID 等非 JSON 原生类型统一转字符串。

    在册缺陷（本包实测）：首版直接 json.dumps(probe) 遇 Date/Decimal 列时整批探针崩
    （TypeError: Object of type date is not JSON serializable）；探针崩掉等于把可用读数
    一起废掉，而本役判据红线要求"读失败必须显式报红"，两者混在一起就分不清是没数还是崩了。
    刻意用鸭子类型（isoformat / numbers.Number）而非 datetime.date 字面量：
    本文件下方 `from datetime import datetime` 会把模块名 datetime 遮蔽成类，
    写 `datetime.date` 会 AttributeError（本包实测踩过一次）。
    """
    import numbers

    if hasattr(v, "isoformat"):
        return str(v.isoformat())
    if isinstance(v, numbers.Number) and not isinstance(v, (int, float, bool)):
        return format(v, "f")  # Decimal：定点字符串，禁科学计数法污染对账
    return str(v)


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="W-180.4 CH 读数标准探针（失败显式报红，禁静默降级）")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sql", help="一条只读 SQL")
    g.add_argument("--count", metavar="TABLE", help="表计数（走 count_strict）")
    g.add_argument("--file", help="探测清单文件，每行一条 SQL（# 开头注释）")
    ap.add_argument("--where", default="", help="配合 --count 的 WHERE 条件（不含 WHERE 关键字）")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument(
        "--out-dir",
        default=str(_REPO_ROOT / ".runtime" / "tmp" / "ch_probe"),
        help="JSONL 产物目录（.runtime/tmp 走 TTL 纪律，禁写生产路径）",
    )
    ap.add_argument("--json", action="store_true", help="stdout 出 pretty JSON")
    args = ap.parse_args(argv)

    probes: list[dict] = []
    if args.sql:
        probes.append(probe_sql(args.sql, args.timeout))
    elif args.count:
        probes.append(probe_count(args.count, args.where, args.timeout))
    else:
        lines = [ln.strip() for ln in Path(args.file).read_text(encoding="utf-8").splitlines()]
        for ln in lines:
            if not ln or ln.startswith("#"):
                continue
            probes.append(probe_sql(ln, args.timeout))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ch_probe_{stamp}.jsonl"
    out_path.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in probes), encoding="utf-8")

    for p in probes:
        if args.json:
            print(json.dumps(p, ensure_ascii=False, indent=2, default=_jsonable))
        else:
            print(json.dumps(p, ensure_ascii=False))
    fails = [p for p in probes if p["outcome"] == "fail"]
    empties = [p for p in probes if p["outcome"] == "empty"]
    print(
        f"[PROBE] 产物={out_path} 共 {len(probes)} 次：ok={len(probes) - len(fails) - len(empties)} "
        f"empty(真空,已确证)={len(empties)} fail(失败,已报红)={len(fails)}",
        file=sys.stderr,
    )
    if fails:
        for p in fails:
            print(f"[RED] 探测失败（禁降级为无数据）: {p['sql_raw'][:120]} -> {p['error']}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
