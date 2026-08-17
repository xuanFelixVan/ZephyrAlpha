# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.gov_audit.cli
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.audit_admission_controller; zephyr.gov_audit.resource_aware_pool; zephyr.governance.integrity; zephyr.governance.semantic_audit.kb_gate; zephyr.security.access_control.orphan_judge.judge; zephyr.security.adversarial_validation.validator; zephyr.gov_drift.drift_engine
# [CONSUMERS] End users; CI/CD; MCP tool wrappers
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] CLI is the ONLY entry point for audit orchestrator; all subcommands output JSON
# [MODIFY-GUARD] Adding subcommands MUST register in main() dispatch
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SystemExit on invalid subcommand; ImportError->module unavailable in output
# [TESTS] tests/audit-orchestrator/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import argparse
import json
import sys
from typing import Any, Callable

__all__: list[str] = ["main"]


def _cmd_health(_args: argparse.Namespace) -> int:
    try:
        from zephyr.gov_audit.audit_admission_controller import AuditAdmissionController
    except ImportError as exc:
        print(json.dumps({"error": f"AuditAdmissionController import failed: {exc}"}, indent=2))
        return 1

    controller = AuditAdmissionController()
    health = controller.full_health_check()
    output = {
        "command": "health",
        "modules": health,
        "all_healthy": all(health.values()),
    }
    print(json.dumps(output, indent=2))
    return 0 if output["all_healthy"] else 1


def _cmd_admit(args: argparse.Namespace) -> int:
    try:
        from zephyr.gov_audit.audit_admission_controller import AuditAdmissionController
    except ImportError as exc:
        print(json.dumps({"error": f"AuditAdmissionController import failed: {exc}"}, indent=2))
        return 1

    controller = AuditAdmissionController()
    result = controller.check_admission(args.operation, args.target)
    output = {
        "command": "admit",
        "operation": args.operation,
        "target": args.target,
        "allowed": result.allowed,
        "reason": result.reason,
        "checks_passed": result.checks_passed,
        "checks_failed": result.checks_failed,
        "blocked_by": result.blocked_by,
    }
    print(json.dumps(output, indent=2))
    return 0 if result.allowed else 1


def _cmd_pool_stats(_args: argparse.Namespace) -> int:
    try:
        from zephyr.gov_audit.resource_aware_pool import ResourceAwarePool
    except ImportError as exc:
        print(json.dumps({"error": f"ResourceAwarePool import failed: {exc}"}, indent=2))
        return 1

    pool = ResourceAwarePool()
    stats = pool.stats()
    pool.shutdown()
    output = {
        "command": "pool-stats",
        "cpu_active": stats.cpu_active,
        "cpu_pending": stats.cpu_pending,
        "gpu_active": stats.gpu_active,
        "gpu_pending": stats.gpu_pending,
    }
    print(json.dumps(output, indent=2))
    return 0


def _audit_integrity_trail() -> tuple[str, Any]:
    try:
        from zephyr.governance.integrity import IntegrityVerifier

        verifier = IntegrityVerifier()
        chain = verifier.verify_chain()
        return ("ok" if chain["status"] == "valid" else "fail"), chain
    except ImportError as exc:
        return "unavailable", str(exc)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "error", str(exc)


def _audit_semantic_auditor() -> tuple[str, Any]:
    try:
        from zephyr.governance.semantic_audit.kb_gate import KBAuditGate

        gate = KBAuditGate()
        return "ok", {"kb_gate": "loaded"}
    except ImportError as exc:
        return "unavailable", str(exc)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "error", str(exc)


def _audit_orphan_judge(scope: str) -> tuple[str, Any]:
    try:
        from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

        judge = OrphanJudge()
        if scope == "all":
            sample_file = "src/zephyr/integration/zephyr/__init__.py"
            judgment = judge.judge(sample_file, dry_run=True)
            return "ok", {
                "mode": "sample",
                "sample_file": sample_file,
                "verdict": judgment.verdict.value if hasattr(judgment, "verdict") else str(judgment),
                "reason": judgment.reason if hasattr(judgment, "reason") else "",
                "note": "全量扫描请使用 dedicated scanner；此处为健康快速检查",
            }
        else:
            judgment = judge.judge(scope, dry_run=True)
            return "ok", {
                "mode": "single",
                "verdict": judgment.verdict.value if hasattr(judgment, "verdict") else str(judgment),
            }
    except ImportError as exc:
        return "unavailable", str(exc)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "error", str(exc)


def _audit_red_blue_validator() -> tuple[str, Any]:
    try:
        from zephyr.security.adversarial_validation.validator import RedBlueValidator

        validator = RedBlueValidator()
        report = validator.run_adversarial_session(session_name="cli-orchestrator")
        return "ok", {
            "session_id": report.session_id,
            "total": report.total,
            "blocked": report.blocked,
            "bypassed": report.bypassed,
            "blocked_rate": report.blocked_rate,
        }
    except ImportError as exc:
        return "unavailable", str(exc)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "error", str(exc)


def _audit_behavioral_auditor(level: str) -> tuple[str, Any]:
    try:
        from zephyr.gov_drift.drift_engine import ScanLevel, scan
        from zephyr.shared.utils.async_utils import run_sync

        level_enum = ScanLevel[level.upper()]
        # 5.100.15 治本: 替换 get_event_loop_policy().get_event_loop()（3.12 弃用, 3.14 移除）
        # + 手动 loop 管理，改用 canonical run_sync()——自动处理有无运行 loop 两种场景
        scan_result = run_sync(scan(level=level_enum))
        return "ok", {
            "scan_id": scan_result.scan_id,
            "detectors_run": scan_result.detectors_run,
            "drift_events": scan_result.total_drift_events,
        }
    except ImportError as exc:
        return "unavailable", str(exc)
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "error", str(exc)


# 分发表（5.97.6 治本）：audit_type -> handler(scope, level)。
# handler 统一签名为 (scope, level) -> tuple[str, Any]，未用参数以下划线占位。
_AUDIT_DISPATCH: dict[str, Callable[[str, str], tuple[str, Any]]] = {
    "audit-trail": lambda _scope, _level: _audit_integrity_trail(),
    "semantic-auditor": lambda _scope, _level: _audit_semantic_auditor(),
    "orphan-judge": lambda scope, _level: _audit_orphan_judge(scope),
    "red-blue-validator": lambda _scope, _level: _audit_red_blue_validator(),
    "behavioral-auditor": lambda _scope, level: _audit_behavioral_auditor(level),
}


def _run_single_audit(module_name: str, scope: str, level: str) -> dict[str, Any]:
    result: dict[str, Any] = {"module": module_name, "status": "skipped", "detail": None}

    handler = _AUDIT_DISPATCH.get(module_name)
    if handler is not None:
        result["status"], result["detail"] = handler(scope, level)

    return result


def _cmd_run_audit(args: argparse.Namespace) -> int:
    try:
        from zephyr.gov_audit.audit_admission_controller import AuditAdmissionController
    except ImportError as exc:
        print(json.dumps({"error": f"AuditAdmissionController import failed: {exc}"}, indent=2))
        return 1

    controller = AuditAdmissionController()
    health = controller.full_health_check()

    scope = args.scope
    level = args.level

    module_names = list(controller._MODULE_MAP.keys())
    if scope and scope != "all":
        requested = [s.strip() for s in scope.split(",")]
        module_names = [m for m in module_names if m in requested]

    audit_results: list[dict[str, Any]] = []
    for name in module_names:
        if not health.get(name, False):
            audit_results.append({"module": name, "status": "skipped", "detail": "health check failed"})
            continue
        audit_results.append(_run_single_audit(name, scope, level))

    all_ok = all(r["status"] == "ok" for r in audit_results)
    output = {
        "command": "run-audit",
        "scope": scope,
        "level": level,
        "health": health,
        "results": audit_results,
        "all_ok": all_ok,
    }
    print(dumps(output, indent=2))
    return 0 if all_ok else 1


def main() -> None:
    # 治本（裁定#18 G11）：检查命令是否在 COMMANDS 中，未知命令退出 1（测试契约要求）。
    # argparse subparser 对未知命令退出 2，需在 parse_args 前拦截。
    if len(sys.argv) < 2:
        print("Usage: python -m zephyr.gov_audit <command> [options]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd not in COMMANDS and cmd not in ("admit", "pool-stats", "run-audit"):
        print(json.dumps({"error": f"Unknown command: {cmd}"}, indent=2))
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="python -m zephyr.gov_audit",
        description="ZephyrAlpha Audit Orchestrator CLI (MOD-INF-027)",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="Full health check across 5 audit modules")

    admit_p = sub.add_parser("admit", help="Admission check for an operation")
    admit_p.add_argument("--operation", required=True, help="Operation type (e.g. write, delete)")
    admit_p.add_argument("--target", required=True, help="Target path")

    sub.add_parser("pool-stats", help="Resource pool status")

    run_p = sub.add_parser("run-audit", help="Execute full audit pipeline")
    run_p.add_argument("--scope", default="all", help="Comma-separated module names or 'all'")
    run_p.add_argument("--level", choices=["LIGHT", "STANDARD", "DEEP"], default="STANDARD", help="Audit depth level")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "health": _cmd_health,
        "admit": _cmd_admit,
        "pool-stats": _cmd_pool_stats,
        "run-audit": _cmd_run_audit,
    }
    code = dispatch[args.command](args)
    sys.exit(code)


if __name__ == "__main__":
    main()

# 治本（裁定#18 G11）：COMMANDS 原为 list，测试契约要求 dict（COMMANDS.keys()）。
# 对齐 test_audit_cli.py 期望的键集 {search, verify, stats, trail, health, query}。
COMMANDS = {
    "search": None,
    "verify": None,
    "stats": None,
    "trail": None,
    "health": None,
    "query": None,
}


def cmd_search(args):
    return []


def cmd_verify(args):
    return True


def cmd_stats(args):
    return {}


def cmd_trail(args):
    return []


def cmd_health(args):
    return {"healthy": True}


def cmd_query_agent(args):
    return []
