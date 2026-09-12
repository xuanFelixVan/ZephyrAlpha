# [BLUEPRINT] MOD-BT-078 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.strategy_screen_query
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; argparse
# [CONSUMERS] 策略入库线消费端（C5 差异化/策略改造回看/Owner 台账查询）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 台账只读（本工具禁写）；追溯链=C2 行→C4 行→run 档案→原文/翻译件（逐段存在性核验）；
#   策略名含逗号/中文，输出一律 JSON 或带引号列（禁裸 TSV）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账不可达)；SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_strategy_screen_query.py
# [A_module] module_id=MOD-BT-078 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_screen 台账查询器——策略失败原因/成绩/追溯链一站式只读查询。

背景：955 行台账=597 份原文（C2 批筛入/筛出）+358 个唯一策略（C4 批翻译/挂起）。
Owner 需求：所有策略（含失败/挂起）的判定与理由可查询可追溯；日后改造复测时能翻到全史。

子命令:
  summary                          批次×判定×理由码分布总览
  trace <strategy_id|md5|名片段>   单策略全史：C2 行+C4 行+run 档案+原文/翻译件存在性
  failed [--reason CODE] [--limit N] [--json]  失败/挂起清单（改造候选检索）
  scored [--min-sharpe X] [--json] 已批测成绩单（DSR 排序）

用法: python scripts/backtest/strategy_screen_query.py trace 6a6ec8869ddb
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_RUNS = _ROOT / "data" / "backtest_artifacts" / "runs"

_TABLE = "c1_backtest.strategy_screen"


_client: Any = None


def _q(sql: str) -> list[tuple]:
    """只读查询（进程内单客户端缓存，退出时关闭——禁 socket 泄漏）。"""
    global _client
    if _client is None:
        from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        from clickhouse_driver import Client

        _client = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                         user=cfg.get("user", "default"), password=cfg.get("password", ""),
                         connect_timeout=5)
        import atexit

        atexit.register(_client.disconnect)
    return _client.execute(sql)


def cmd_summary(_args: argparse.Namespace) -> int:
    out: dict[str, Any] = {"total": _q(f"SELECT count() FROM {_TABLE}")[0][0],
                           "uniq_strategy": _q(f"SELECT uniqExact(strategy_id) FROM {_TABLE}")[0][0],
                           "batches": []}
    for batch, verdict, n in _q(
        f"SELECT screen_batch, verdict, count() FROM {_TABLE} GROUP BY screen_batch, verdict ORDER BY screen_batch, verdict"
    ):
        out["batches"].append({"batch": batch, "verdict": verdict, "rows": n})
    reasons = [
        {"batch": b, "reason": r, "rows": n}
        for b, r, n in _q(
            f"SELECT screen_batch, verdict_reason, count() FROM {_TABLE} WHERE verdict LIKE 'deferred%' OR verdict='rejected' "
            f"GROUP BY screen_batch, verdict_reason ORDER BY count() DESC LIMIT 50"
        )
    ]
    out["failure_reasons"] = reasons
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def _resolve(pattern: str) -> list[str]:
    """策略 ID 解析：精确 ID / 12 位 md5 / 名称片段（回退到 CSV 清单模糊匹配）。"""
    ids = {r[0] for r in _q(
        f"SELECT DISTINCT strategy_id FROM {_TABLE} WHERE strategy_id LIKE '%{pattern}%'")}
    if ids:
        return sorted(ids)
    import csv as _csv

    manifest = _ROOT / "data" / "strategy_intake" / "raw_manifest.csv"
    if manifest.exists():
        with manifest.open(encoding="utf-8-sig", newline="") as f:
            md5s = {r["md5_12"] for r in _csv.DictReader(f) if pattern.lower() in r["orig_name"].lower()}
        if md5s:
            return sorted(f"CAND-{m}" for m in md5s)
    return []


def cmd_trace(args: argparse.Namespace) -> int:
    ids = _resolve(args.pattern)
    if not ids:
        print(json.dumps({"error": "no match", "pattern": args.pattern}, ensure_ascii=False))
        return 1
    results = []
    for sid in ids:
        rows = _q(
            f"SELECT run_id, screen_batch, verdict, verdict_reason, translated, is_sharpe, deflated_sharpe, "
            f"max_drawdown, turnover, source_file, notes, screened_at FROM {_TABLE} "
            f"WHERE strategy_id = '{sid}' ORDER BY screened_at"
        )
        trail = []
        for run_id, batch, verdict, reason, translated, sharpe, dsr, mdd, to, src, notes, at in rows:
            entry: dict[str, Any] = {
                "run_id": run_id, "batch": batch, "verdict": verdict, "reason": reason,
                "translated": translated, "is_sharpe": sharpe, "deflated_sharpe": dsr,
                "max_drawdown": mdd, "turnover": to, "source_file": src, "notes": notes,
                "at": str(at),
            }
            art = _RUNS / str(run_id)
            entry["run_archive_exists"] = art.exists()
            if str(src).startswith("scripts/backtest/translated/") and (_ROOT / str(src)).exists():
                entry["translation_file"] = src
            trail.append(entry)
        results.append({"strategy_id": sid, "history": trail})
    print(json.dumps(results, ensure_ascii=False, indent=1, default=str))
    return 0


def cmd_failed(args: argparse.Namespace) -> int:
    cond = "verdict IN ('deferred_c4', 'rejected')"
    if args.reason:
        cond += f" AND verdict_reason LIKE '%{args.reason}%'"
    cond += f" AND screen_batch = '{args.batch}'" if args.batch else ""
    limit = args.limit or 100
    rows = _q(
        f"SELECT strategy_id, screen_batch, verdict, verdict_reason, source_file, notes FROM {_TABLE} "
        f"WHERE {cond} ORDER BY strategy_id LIMIT {limit}"
    )
    out = [{"strategy_id": a, "batch": b, "verdict": v, "reason": rr, "source_file": sf, "notes": nt}
           for a, b, v, rr, sf, nt in rows]
    print(json.dumps({"count": len(out), "items": out}, ensure_ascii=False, indent=1, default=str))
    return 0


def cmd_scored(args: argparse.Namespace) -> int:
    cond = f"verdict='translated_c4' AND screen_batch = '{args.batch}'" if args.batch else "verdict='translated_c4'"
    cond += f" AND is_sharpe >= {args.min_sharpe}" if args.min_sharpe is not None else ""
    rows = _q(
        f"SELECT strategy_id, is_sharpe, deflated_sharpe, max_drawdown, turnover, source_file, notes FROM {_TABLE} "
        f"WHERE {cond} ORDER BY is_sharpe DESC"
    )
    out = [{"strategy_id": a, "is_sharpe": b, "deflated_sharpe": c, "max_drawdown": d,
            "turnover": e, "translation_file": f, "notes": n} for a, b, c, d, e, f, n in rows]
    print(json.dumps({"count": len(out), "items": out}, ensure_ascii=False, indent=1, default=str))
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="strategy_screen 台账只读查询器")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("summary", help="批次×判定×理由码分布")
    t = sub.add_parser("trace", help="单策略全史追溯")
    t.add_argument("pattern", help="strategy_id / md5_12 / 原文名片段")
    f = sub.add_parser("failed", help="失败/挂起清单")
    f.add_argument("--reason", default=None, help="理由码过滤（如 fundamental_gate）")
    f.add_argument("--batch", default=None, help="批次过滤")
    f.add_argument("--limit", type=int, default=100)
    s = sub.add_parser("scored", help="已批测成绩单")
    s.add_argument("--min-sharpe", type=float, default=None)
    s.add_argument("--batch", default=None)
    args = p.parse_args()
    rc = {"summary": cmd_summary, "trace": cmd_trace, "failed": cmd_failed, "scored": cmd_scored}[args.cmd](args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
