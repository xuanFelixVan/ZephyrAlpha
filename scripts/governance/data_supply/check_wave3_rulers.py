# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/00_master_skeleton.md | W-102（三把尺常设化）
# [MODULE] scripts.governance.data_supply.check_wave3_rulers
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.data_supply.{supply_sources,strict_truth_reader,false_green_crosscheck,supply_conservation,no_cache_endorsement}, scripts.governance._shared.constants
# [CONSUMERS] [待登记] .github/workflows/governance.yml 新增一步（见 registration_needs.yaml）; 人工 CLI; pytest tests/governance/data_supply/*
# [STARTUP] manual
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#   （按需对账窗工具；permanent+manual 组合触发 PERM-TRIGGER 铁律，故归 task_bound）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] rc 语义：--check 0=三把尺全绿 1=有违规红项 2=读数/装载失败必抛后落 rc=2（禁把失败洗成 0）; --counterfactual 0=控制组全部如期转红（尺是活的） 1=至少一把尺点不红（尺已退化为装饰件） 2=控制组自身异常
# [A_module] module_id=MOD-GOV-DS-CLI | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 一次性 CLI 工具，非常驻服务
"""W-102 三把尺的常设化 CI 入口（波 3.2 / 3.3 / W-102）。

Usage:
    python scripts/governance/data_supply/check_wave3_rulers.py --check
    python scripts/governance/data_supply/check_wave3_rulers.py --check --ruler false-green
    python scripts/governance/data_supply/check_wave3_rulers.py --counterfactual
    python scripts/governance/data_supply/check_wave3_rulers.py --check --offline

`--offline` 只跑不触库的第三把尺（禁缓存背书），用于 CI 无 ClickHouse 的槽位。
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import traceback
from pathlib import Path
from typing import Sequence

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
for _p in (str(_ROOT), str(_ROOT / "scripts" / "governance")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from scripts.governance.data_supply import no_cache_endorsement as _nocache  # noqa: E402
from scripts.governance.data_supply.false_green_crosscheck import evaluate as _evaluate_fg  # noqa: E402
from scripts.governance.data_supply.false_green_crosscheck import run_counterfactual as _cf_fg  # noqa: E402
from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader  # noqa: E402
from scripts.governance.data_supply.supply_conservation import evaluate as _evaluate_cons  # noqa: E402
from scripts.governance.data_supply.supply_conservation import red_findings as _cons_reds  # noqa: E402
from scripts.governance.data_supply.supply_conservation import run_counterfactual as _cf_cons  # noqa: E402
from scripts.governance.data_supply.supply_sources import (  # noqa: E402
    MissingSourceError,
    build_downstream_map,
    load_declared_gap_index,
    load_ledger_runs,
    load_sentinel_legs,
    load_task_specs,
    open_progress_store,
)

RULERS = ("false-green", "conservation", "no-cache")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Wave-3 data-supply rulers (3.2 / 3.3 / W-102)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="run rulers against live declared/arrived truth")
    mode.add_argument(
        "--counterfactual",
        action="store_true",
        help="run each ruler's control group; rc!=0 means a ruler cannot redden",
    )
    ap.add_argument("--ruler", choices=("all",) + RULERS, default="all")
    ap.add_argument("--as-of", default="", help="YYYY-MM-DD business anchor (default: UTC today)")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument("--limit", type=int, default=5000, help="max task_runs rows pulled through the host API")
    ap.add_argument("--offline", action="store_true", help="skip the two rulers that must read ClickHouse")
    ap.add_argument("--ledger", default="", help="override task_runs db path (tests/tmp fixtures)")
    return ap


def _as_of(text: str) -> dt.date:
    return dt.date.fromisoformat(text) if text else dt.datetime.now(dt.timezone.utc).date()


def _load_declarations(root: Path):
    specs = load_task_specs(root)
    return specs, load_sentinel_legs(root), load_declared_gap_index(root)


def _run_no_cache(root: Path) -> int:
    verdict = _nocache.evaluate(root, lambda probe: StrictTruthReader(projection=probe))
    for f in verdict.findings:
        print(f"[no-cache] RED {f.path}:{f.lineno} {f.code} :: {f.detail}")
    print(f"[no-cache] scanned={verdict.scanned_files} files probe_reads={verdict.probe_reads}")
    return EXIT_PASS if verdict.ok else EXIT_FINDINGS


def _run_false_green(root: Path, as_of: dt.date, limit: int, ledger: str) -> int:
    specs, legs, _gaps = _load_declarations(root)
    store = open_progress_store(root, Path(ledger) if ledger else None)
    runs = load_ledger_runs(
        store,
        since=dt.datetime.combine(as_of - dt.timedelta(days=6), dt.time(0, 0), tzinfo=dt.timezone.utc),
        limit=limit,
    )
    verdict = _evaluate_fg(runs, specs, legs, StrictTruthReader(), as_of=as_of, downstream=build_downstream_map(specs))
    for f in verdict.findings:
        print(f"[false-green] {f.severity} {f.code} task={f.task_id or '-'} table={f.table or '-'} :: {f.detail}")
    print(
        f"[false-green] checked_runs={verdict.checked_runs} red={len(verdict.red)} downgraded_tasks={list(verdict.downgraded_tasks)}"
    )
    print(f"[false-green] 降级下游表（不得据本窗回执背书）={list(verdict.downgraded_tables)}")
    return EXIT_PASS if verdict.ok else EXIT_FINDINGS


def _run_conservation(root: Path, as_of: dt.date, window_days: int, limit: int, ledger: str) -> int:
    specs, legs, gap_index = _load_declarations(root)
    store = open_progress_store(root, Path(ledger) if ledger else None)
    runs = list(load_ledger_runs(store, since=None, limit=limit))
    reports = _evaluate_cons(
        specs=specs,
        legs_by_table=legs,
        runs=runs,
        reader=StrictTruthReader(),
        lo=as_of - dt.timedelta(days=window_days - 1),
        hi=as_of,
        gap_index=gap_index,
    )
    reds = _cons_reds(reports)
    for rep in reports:
        for f in rep.findings:
            print(f"[conservation] {f.severity} {f.code} table={f.table or '-'} :: {f.detail}")
    print(
        f"[conservation] tables={len(reports)} red={len(reds)} "
        f"declared_rows={sum(r.rows_declared for r in reports)} arrived_rows={sum(r.rows_arrived for r in reports)}"
    )
    return EXIT_PASS if not reds else EXIT_FINDINGS


def _check_sequence(args: argparse.Namespace) -> Sequence[str]:
    if args.offline:
        return ("no-cache",) if args.ruler == "all" else (args.ruler,)
    return RULERS if args.ruler == "all" else (args.ruler,)


def run_check(args: argparse.Namespace, root: Path) -> int:
    worst = EXIT_PASS
    for ruler in _check_sequence(args):
        rc = _dispatch_check(ruler, root, args)
        worst = max(worst, rc)
    return worst


def _dispatch_check(ruler: str, root: Path, args: argparse.Namespace) -> int:
    if ruler == "no-cache":
        return _run_no_cache(root)
    if ruler == "false-green":
        return _run_false_green(root, _as_of(args.as_of), args.limit, args.ledger)
    return _run_conservation(root, _as_of(args.as_of), args.window_days, args.limit, args.ledger)


def _show(ctrl) -> int:
    verdict = getattr(ctrl, "passed", ctrl.reddened)
    flag = "OK（负控制转红、正控制保持绿）" if verdict else "DEFECT（控制组不如期显影＝尺已退化为装饰件）"
    print(f"[counterfactual] {ctrl.ruler} -> {flag} red_codes={list(ctrl.codes)} probe_reads={ctrl.observed_reads}")
    print(f"    {ctrl.detail}")
    downgraded = getattr(ctrl, "downgraded_tasks", ())
    if downgraded:
        print(f"    点名降级下游（其窗内回执不得背书）={list(downgraded)}")
    return EXIT_PASS if verdict else EXIT_FINDINGS


def run_counterfactual(args: argparse.Namespace) -> int:
    picked = RULERS if args.ruler == "all" else (args.ruler,)
    worst = EXIT_PASS
    for ruler in picked:
        if ruler == "no-cache":
            worst = max(worst, _show(_nocache.run_counterfactual()))
        elif ruler == "false-green":
            worst = max(worst, _show(_cf_fg(_as_of(args.as_of) if args.as_of else None)))
        else:
            worst = max(worst, _show(_cf_cons(_as_of(args.as_of) if args.as_of else None)))
    return worst


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _ROOT
    try:
        if args.counterfactual:
            return run_counterfactual(args)
        return run_check(args, root)
    except MissingSourceError as exc:
        print(f"[error] 声明侧真源不可用（禁降级放行）: {exc}")
        return EXIT_ERROR
    except Exception as exc:  # noqa: BLE001 — 判据类失败必抛后以 rc=2 显影（W-180 红线）
        print(f"[error] {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=3)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
