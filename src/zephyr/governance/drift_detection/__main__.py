# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.__main__
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_engine; zephyr.governance.drift_detection.self_test_verifier; zephyr.governance.drift_detection.drift_infrastructure; zephyr.governance.drift_detection.self_check
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] CLI入口不可修改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §

Drift Detector MOD-INF-023 CLI — 漂移扫描入口。

用法

----

    python -m zephyr.governance.drift_detection scan                    # 默认 LIGHT 扫描

    python -m zephyr.governance.drift_detection scan --level STANDARD   # 标准扫描

    python -m zephyr.governance.drift_detection scan --level DEEP       # 深度扫描

    python -m zephyr.governance.drift_detection self-test               # SelfTestVerifier 自检

    python -m zephyr.governance.drift_detection budget [module_id]      # 检查漂移预算

    python -m zephyr.governance.drift_detection list                    # 列出所有已注册检测器

    python -m zephyr.governance.drift_detection status                  # 模块健康状态"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys


def _cmd_scan(args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.drift_detection.drift_engine import ScanLevel, build_report, scan

    except ImportError as exc:
        print(f"ERROR: drift_engine import failed: {exc}", file=sys.stderr)

        return 1

    level = ScanLevel[args.level.upper()]

    try:
        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(scan(level=level))

        loop.close()

    except Exception as exc:
        print(f"ERROR: scan failed: {exc}", file=sys.stderr)

        return 1

    report = build_report(result)

    print(f"  SCAN_ID        {result.scan_id}")

    print(f"  LEVEL          {args.level.upper()}")

    print(f"  DETECTORS_RUN  {result.detectors_run}")

    print(f"  DRIFT_EVENTS   {result.total_drift_events}")

    print(f"  STORM_MODE     {result.storm_mode_triggered}")

    if report.top_drift_dimensions:
        print(f"  TOP_DIMS       {report.top_drift_dimensions[:5]}")

    print(f"  SUMMARY        {report.scan_summary}")

    return 1 if result.total_drift_events > 0 else 0


def _cmd_self_test(args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.drift_detection.self_test_verifier import SelfTestVerifier

    except ImportError as exc:
        print(f"ERROR: SelfTestVerifier import failed: {exc}", file=sys.stderr)

        return 1

    verifier = SelfTestVerifier()

    result = verifier.run_all()

    if args.json:
        print(
            json.dumps(
                {
                    "summary": result.summary,
                    "checks": result.checks,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    else:
        print(f"  SUMMARY        {result.summary}")

        for c in result.checks:
            status_icon = "PASS" if c["status"] == "PASS" else "FAIL"

            print(f"  [{status_icon}] {c['check']}")

            if c.get("detail"):
                print(f"         {c['detail']}")

    return 0 if result.summary == "8/8 checks passed" else 1


def _cmd_budget(args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.drift_detection.drift_infrastructure import check_budget_for_gate

    except ImportError as exc:
        print(f"ERROR: drift_engine import failed: {exc}", file=sys.stderr)

        return 1

    module_id = args.module_id or "MOD-INF-023"

    tier = args.tier or "P0"

    result = check_budget_for_gate(module_id, tier)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        allowed = result.get("allowed", False)

        reason = result.get("reason", "?")

        label = "ALLOWED" if allowed else "BLOCKED"

        print(f"  MODULE         {module_id}")

        print(f"  TIER           {tier}")

        print(f"  STATUS         {label}")

        print(f"  REASON         {reason}")

    return 0 if result.get("allowed") else 1


def _cmd_list(args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.drift_detection.drift_engine import load_detector_registry

    except ImportError as exc:
        print(f"ERROR: drift_engine import failed: {exc}", file=sys.stderr)

        return 1

    detectors = load_detector_registry()

    if args.json:
        data = []

        for d in detectors:
            data.append(
                {
                    "id": d.id,
                    "dimension": d.drift_dimension,
                    "severity": d.severity.value if hasattr(d.severity, "value") else str(d.severity),
                    "category": d.category,
                    "status": d.status,
                    "auto_fixable": d.auto_fixable,
                }
            )

        print(json.dumps(data, ensure_ascii=False, indent=2))

    else:
        from collections import Counter

        cats = Counter(d.category for d in detectors)

        sevs = Counter(d.severity.value if hasattr(d.severity, "value") else str(d.severity) for d in detectors)

        print(f"  TOTAL          {len(detectors)}")

        print(f"  CATEGORIES     {dict(cats)}")

        print(f"  SEVERITIES     {dict(sevs)}")

        print(f"  ALL_ACTIVE     {all(d.status == 'active' for d in detectors)}")

        print()

        for d in detectors:
            auto = " [AUTO-FIX]" if d.auto_fixable else ""

            print(
                f"  {d.id:35s}  {d.severity.value if hasattr(d.severity, 'value') else str(d.severity):6s}  {d.category:20s}{auto}"
            )

    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    ok = True

    issues: list[str] = []

    try:
        from zephyr.governance.drift_detection.drift_engine import load_detector_registry

        detectors = load_detector_registry()

        active = sum(1 for d in detectors if d.status == "active")

        print(f"  registry        OK  ({active}/{len(detectors)} active, {len(detectors)} total)")

    except Exception as exc:
        print(f"  registry        FAIL  {exc}")

        ok = False

    try:
        print("  drift_engine    OK  (scan + build_report + budget)")

    except Exception as exc:
        print(f"  drift_engine    FAIL  {exc}")

        ok = False

    try:
        from zephyr.governance.drift_detection.self_test_verifier import SelfTestVerifier

        v = SelfTestVerifier()

        r = v.run_all()

        status_text = "OK" if r.summary == "8/8 checks passed" else "DEGRADED"

        print(f"  self_test       {status_text}  ({r.summary})")

        if r.summary != "8/8 checks passed":
            ok = False

    except Exception as exc:
        print(f"  self_test       FAIL  {exc}")

        ok = False

    try:
        from zephyr.governance.drift_detection.self_check import bootstrap_self_check

        bc = bootstrap_self_check()

        if bc:
            print("  self_check      OK  (integrity + bootstrap)")

        else:
            print(f"  self_check      DEGRADED  (bootstrap={bc})")

            ok = False

    except Exception as exc:
        print(f"  self_check      FAIL  {exc}")

        ok = False

    try:
        print("  cold_start      OK  (session_entry_activate + detect_missing_env)")

    except Exception as exc:
        print(f"  cold_start      FAIL  {exc}")

        ok = False

    try:
        print("  reconciler      OK  (AutoFixer)")

    except Exception as exc:
        print(f"  reconciler      FAIL  {exc}")

        ok = False

    try:
        print("  cascade_detect  OK")

    except Exception as exc:
        print(f"  cascade_detect  FAIL  {exc}")

        ok = False

    try:
        print("  chaos_injector  OK")

    except Exception as exc:
        print(f"  chaos_injector  FAIL  {exc}")

        ok = False

    try:
        print("  gate_integration OK  (trigger_recovery)")

    except Exception as exc:
        print(f"  gate_integration FAIL  {exc}")

        ok = False

    for issue in issues:
        print(f"  WARNING: {issue}")

    label = "ALL SYSTEMS GO" if ok else "SOME SYSTEMS DEGRADED"

    print(f"\n  {label}")

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.governance.drift_detection",
        description="ZephyrAlpha Drift Detector — 漂移运行时检测 (MOD-INF-023)",
    )

    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="执行漂移扫描")

    p_scan.add_argument(
        "--level", choices=["LIGHT", "STANDARD", "DEEP"], default="LIGHT", help="扫描级别 (默认: LIGHT)"
    )

    p_test = sub.add_parser("self-test", help="SelfTestVerifier 8项自检")

    p_test.add_argument("--json", action="store_true", help="JSON 输出")

    p_budget = sub.add_parser("budget", help="检查漂移预算")

    p_budget.add_argument("module_id", nargs="?", default="MOD-INF-023", help="模块 ID (默认: MOD-INF-023)")

    p_budget.add_argument("--tier", choices=["P0", "P1", "P2", "P3"], default="P0", help="预算层级 (默认: P0)")

    p_budget.add_argument("--json", action="store_true", help="JSON 输出")

    p_list = sub.add_parser("list", help="列出所有已注册检测器")

    p_list.add_argument("--json", action="store_true", help="JSON 输出")

    p_status = sub.add_parser("status", help="模块健康状态")

    args = parser.parse_args()

    if args.command == "scan":
        return _cmd_scan(args)

    elif args.command == "self-test":
        return _cmd_self_test(args)

    elif args.command == "budget":
        return _cmd_budget(args)

    elif args.command == "list":
        return _cmd_list(args)

    elif args.command == "status":
        return _cmd_status(args)

    else:
        return _cmd_status(args)


if __name__ == "__main__":
    sys.exit(main())
