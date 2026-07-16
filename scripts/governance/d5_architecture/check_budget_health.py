# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/check_budget_health.py | §
# [MODULE] scripts.governance.d5_architecture.check_budget_health
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §16.8
[MODULE] scripts.governance.d5_architecture.check_budget_health
[INVARIANTS] 预算健康检查不可跳过;检查结果必须可机器解析
[MODIFY-GUARD] docs/03_modules/infrastructure_runtime_integration/budget-enforcer/blueprint.md
[CONSUMERS] CI pipeline; AutoRuntime Core
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=HEALTHY; exit 1=WARN; exit 2=CRITICAL; exit 3=ERROR
[TESTS] tests/governance/test_check_budget_health.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: '[BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
  | §16.8'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import sys
from pathlib import Path
from _shared.constants import REPO_ROOT



def check_engine_instantiation() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement import BudgetEngine

        engine = BudgetEngine()
        return {"check": "engine_instantiation", "status": "PASS", "detail": str(type(engine))}
    except Exception as e:
        return {"check": "engine_instantiation", "status": "CRITICAL", "detail": str(e)}


def check_pre_flight() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.budget_models import GateDecision

        from zephyr.governance.financial_governance.budget_enforcement import BudgetEngine

        engine = BudgetEngine()
        result = engine.pre_flight_check("health-check", 100, 0.001)
        if result.decision == GateDecision.DENY:
            return {"check": "pre_flight", "status": "CRITICAL", "detail": f"DENY: {result.reason}"}
        return {"check": "pre_flight", "status": "PASS", "detail": f"decision={result.decision.name}"}
    except Exception as e:
        return {"check": "pre_flight", "status": "CRITICAL", "detail": str(e)}


def check_dimensions() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.budget_models import BudgetDimension

        dims = set(d.value.lower() for d in BudgetDimension)
        required = {"token", "cost", "time"}
        missing = required - dims
        if missing:
            return {"check": "dimensions", "status": "WARN", "detail": f"missing: {missing}"}
        return {"check": "dimensions", "status": "PASS", "detail": "all 3 dimensions present"}
    except Exception as e:
        return {"check": "dimensions", "status": "CRITICAL", "detail": str(e)}


def check_policy_file() -> dict:
    policy_path = REPO_ROOT / "config" / "budget_policy.yaml"
    if not policy_path.exists():
        return {"check": "policy_file", "status": "CRITICAL", "detail": f"not found: {policy_path}"}
    try:
        import yaml

        with open(policy_path, encoding="utf-8") as f:
            yaml.safe_load(f)
        return {"check": "policy_file", "status": "PASS", "detail": "exists and parseable"}
    except Exception as e:
        return {"check": "policy_file", "status": "CRITICAL", "detail": str(e)}


def check_escalation_bridge() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.alerts import BudgetAlert
        from zephyr.governance.escalation.budget_handler import on_budget_alert

        alert = BudgetAlert(alert_id="health-check")
        result = on_budget_alert(alert)
        if result is not None:
            return {"check": "escalation_bridge", "status": "PASS", "detail": "G-CT-006 OK"}
        return {"check": "escalation_bridge", "status": "WARN", "detail": "returned None"}
    except ImportError:
        return {"check": "escalation_bridge", "status": "WARN", "detail": "escalation-engine not available"}
    except Exception as e:
        return {"check": "escalation_bridge", "status": "WARN", "detail": str(e)}


def check_degradation_manager() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.degradation_manager import DegradationManager

        dm = DegradationManager()
        level = dm.state.current_level
        cb_open = dm.circuit_breaker_open
        return {
            "check": "degradation_manager",
            "status": "PASS",
            "detail": f"level={level.name}, circuit_breaker={cb_open}",
        }
    except Exception as e:
        return {"check": "degradation_manager", "status": "CRITICAL", "detail": str(e)}


def check_tamper_log() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.tamper_evident_log import TamperEvidentLog

        log = TamperEvidentLog()
        log.append("health-check", "test-data")
        valid, pos = log.verify()
        if valid:
            return {"check": "tamper_log", "status": "PASS", "detail": f"chain_length={log.chain_length()}, valid=True"}
        return {"check": "tamper_log", "status": "CRITICAL", "detail": f"chain broken at position {pos}"}
    except Exception as e:
        return {"check": "tamper_log", "status": "CRITICAL", "detail": str(e)}


def check_burn_rate_monitor() -> dict:
    try:
        from zephyr.governance.financial_governance.budget_enforcement.burn_rate_monitor import BurnRateMonitor

        monitor = BurnRateMonitor()
        summary = monitor.get_burn_summary()
        return {"check": "burn_rate_monitor", "status": "PASS", "detail": f"windows={len(summary)}"}
    except Exception as e:
        return {"check": "burn_rate_monitor", "status": "WARN", "detail": str(e)}


CHECKS = [
    check_engine_instantiation,
    check_pre_flight,
    check_dimensions,
    check_policy_file,
    check_escalation_bridge,
    check_degradation_manager,
    check_tamper_log,
    check_burn_rate_monitor,
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Budget Enforcer health check")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even on WARN")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = []
    for check_fn in CHECKS:
        results.append(check_fn())

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    exit_code = 0
    for r in results:
        status = r["status"]
        prefix = "✓" if status == "PASS" else ("⚠" if status == "WARN" else "✗")
        print(f"  {prefix} {r['check']}: {r['detail']}")
        if status == "CRITICAL":
            exit_code = 2
        elif status == "WARN" and exit_code == 0:
            exit_code = 1

    if args.warn_only and exit_code == 1:
        exit_code = 0

    print(f"\nResult: {'HEALTHY' if exit_code == 0 else 'WARN' if exit_code == 1 else 'CRITICAL'}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
