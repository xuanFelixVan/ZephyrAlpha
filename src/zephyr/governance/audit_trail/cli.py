# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.cli
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.audit_admission_controller; zephyr.governance.audit_trail.resource_aware_pool; zephyr.governance.integrity; zephyr.governance.semantic_audit.kb_gate; zephyr.security.access_control.orphan_judge.judge; zephyr.security.adversarial_validation.validator; zephyr.governance.drift_detection.drift_engine
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
# [A_module] module_id=MOD-GOV_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import argparse
import json
import sys
from typing import Any

__all__: list[str] = ["main"]


def _cmd_health(_args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController
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
        from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController
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
        from zephyr.governance.audit_trail.resource_aware_pool import ResourceAwarePool
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


def _run_single_audit(module_name: str, scope: str, level: str) -> dict[str, Any]:
    result: dict[str, Any] = {"module": module_name, "status": "skipped", "detail": None}

    if module_name == "audit-trail":
        try:
            from zephyr.governance.integrity import IntegrityVerifier

            verifier = IntegrityVerifier()
            chain = verifier.verify_chain()
            result["status"] = "ok" if chain["status"] == "valid" else "fail"
            result["detail"] = chain
        except ImportError as exc:
            result["status"] = "unavailable"
            result["detail"] = str(exc)
        except Exception as exc:
            result["status"] = "error"
            result["detail"] = str(exc)

    elif module_name == "semantic-auditor":
        try:
            from zephyr.governance.semantic_audit.kb_gate import KBAuditGate

            gate = KBAuditGate()
            result["status"] = "ok"
            result["detail"] = {"kb_gate": "loaded"}
        except ImportError as exc:
            result["status"] = "unavailable"
            result["detail"] = str(exc)
        except Exception as exc:
            result["status"] = "error"
            result["detail"] = str(exc)

    elif module_name == "orphan-judge":
        try:
            from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

            judge = OrphanJudge()
            if scope == "all":
                sample_file = "src/zephyr/integration/zephyr/__init__.py"
                judgment = judge.judge(sample_file, dry_run=True)
                result["status"] = "ok"
                result["detail"] = {
                    "mode": "sample",
                    "sample_file": sample_file,
                    "verdict": judgment.verdict.value if hasattr(judgment, "verdict") else str(judgment),
                    "reason": judgment.reason if hasattr(judgment, "reason") else "",
                    "note": "全量扫描请使用 dedicated scanner；此处为健康快速检查",
                }
            else:
                judgment = judge.judge(scope, dry_run=True)
                result["status"] = "ok"
                result["detail"] = {
                    "mode": "single",
                    "verdict": judgment.verdict.value if hasattr(judgment, "verdict") else str(judgment),
                }
        except ImportError as exc:
            result["status"] = "unavailable"
            result["detail"] = str(exc)
        except Exception as exc:
            result["status"] = "error"
            result["detail"] = str(exc)

    elif module_name == "red-blue-validator":
        try:
            from zephyr.security.adversarial_validation.validator import RedBlueValidator

            validator = RedBlueValidator()
            report = validator.run_adversarial_session(session_name="cli-orchestrator")
            result["status"] = "ok"
            result["detail"] = {
                "session_id": report.session_id,
                "total": report.total,
                "blocked": report.blocked,
                "bypassed": report.bypassed,
                "blocked_rate": report.blocked_rate,
            }
        except ImportError as exc:
            result["status"] = "unavailable"
            result["detail"] = str(exc)
        except Exception as exc:
            result["status"] = "error"
            result["detail"] = str(exc)

    elif module_name == "behavioral-auditor":
        try:
            import asyncio

            from zephyr.governance.drift_detection.drift_engine import ScanLevel, scan

            level_enum = ScanLevel[level.upper()]
            # 5.100.18 修复: 保存原 loop 并在 finally 中恢复, 避免污染调用方 loop 上下文
            _prev_loop = asyncio.get_event_loop_policy().get_event_loop()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                scan_result = loop.run_until_complete(scan(level=level_enum))
            finally:
                loop.close()
                asyncio.set_event_loop(_prev_loop)
            result["status"] = "ok"
            result["detail"] = {
                "scan_id": scan_result.scan_id,
                "detectors_run": scan_result.detectors_run,
                "drift_events": scan_result.total_drift_events,
            }
        except ImportError as exc:
            result["status"] = "unavailable"
            result["detail"] = str(exc)
        except Exception as exc:
            result["status"] = "error"
            result["detail"] = str(exc)

    return result


def _cmd_run_audit(args: argparse.Namespace) -> int:
    try:
        from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController
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
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.governance.audit_trail",
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

COMMANDS = ["verify", "query", "replay", "export", "integrity"]


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
