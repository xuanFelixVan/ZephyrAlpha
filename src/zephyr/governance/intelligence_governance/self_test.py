# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.self_test
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_self_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Escalation Protocol Self-Test — MOD-INF-022.

Atomic self-check that validates the escalation engine's own health.
Used by: cold start STEP 4.8, Phase Manager gate_escalation_protocol, CI/CD.

Run: python -m zephyr.governance.intelligence_governance.self_test [--warn-only] [--json]
Returns: 0 if fully healthy, 1 if degraded, 2 if critical failure.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from enum import Enum


class HealthLevel(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class CheckResult:
    name: str
    passed: bool
    level: HealthLevel = HealthLevel.HEALTHY
    detail: str = ""
    latency_ms: float = 0.0


@dataclass
class SelfTestReport:
    checks: list[CheckResult] = field(default_factory=list)
    total_passed: int = 0
    total_failed: int = 0
    overall: HealthLevel = HealthLevel.HEALTHY
    duration_ms: float = 0.0


def run_self_test() -> SelfTestReport:
    t0 = time.perf_counter()
    report = SelfTestReport()

    check_results: list[CheckResult] = []

    # Check 1: Import chain
    t1 = time.perf_counter()
    try:
        from zephyr.governance.intelligence_governance.delegation_engine import DelegationEngine
        from zephyr.governance.escalation.escalation_engine import EscalationEngine
        from zephyr.governance.escalation.escalation_models import (
            DelegationStrategy,
            EconomicGuard,
            EscalationLevel,
            EscalationState,
            RuleCategory,
        )
        from zephyr.governance.resilience_governance.circuit_breaker import CircuitBreaker, CircuitState

        check_results.append(CheckResult("import_chain", True, detail="All core symbols importable"))
    except ImportError as e:
        check_results.append(CheckResult("import_chain", False, HealthLevel.CRITICAL, str(e)))
    latency = (time.perf_counter() - t1) * 1000

    # Check 2: Engine initialization
    t1 = time.perf_counter()
    try:
        engine = EscalationEngine("self-test", hooks_enabled=False)
        rule_count = len(engine._rules)
        if rule_count < 5:
            check_results.append(
                CheckResult("engine_init", False, HealthLevel.DEGRADED, f"Only {rule_count} rules loaded")
            )
        else:
            check_results.append(CheckResult("engine_init", True, detail=f"{rule_count} rules loaded"))
    except Exception as e:
        check_results.append(CheckResult("engine_init", False, HealthLevel.CRITICAL, str(e)))

    # Check 3: Basic evaluate
    try:
        ev = engine.evaluate(RuleCategory.SECURITY_VIOLATION, "self_test_probe")
        if ev is None:
            check_results.append(CheckResult("evaluate", False, HealthLevel.DEGRADED, "evaluate() returned None"))
        elif ev.level is None:
            check_results.append(CheckResult("evaluate", False, HealthLevel.DEGRADED, "event has no level"))
        else:
            check_results.append(CheckResult("evaluate", True, detail=f"level={ev.level.name}"))
    except Exception as e:
        check_results.append(CheckResult("evaluate", False, HealthLevel.CRITICAL, str(e)))

    # Check 4: Circuit breaker state
    try:
        cb_state = engine.get_circuit_state()
        if cb_state is CircuitState.OPEN:
            check_results.append(CheckResult("circuit_breaker", False, HealthLevel.DEGRADED, "Circuit is OPEN"))
        else:
            check_results.append(CheckResult("circuit_breaker", True, detail=f"state={cb_state.name}"))
    except Exception as e:
        check_results.append(CheckResult("circuit_breaker", False, HealthLevel.CRITICAL, str(e)))

    # Check 5: Economic guard status
    try:
        status = engine.get_economic_status()
        if status.get("hard_limit_reached"):
            check_results.append(CheckResult("economic_guard", False, HealthLevel.DEGRADED, "Hard limit reached"))
        else:
            check_results.append(
                CheckResult(
                    "economic_guard", True, detail=f"consumed={status['consumed_today']}/{status['daily_budget']}"
                )
            )
    except Exception as e:
        check_results.append(CheckResult("economic_guard", False, HealthLevel.CRITICAL, str(e)))

    # Check 6: Delegation engine
    try:
        de = DelegationEngine()
        de.register_delegate("_self_test_probe")
        ev_probe = engine.evaluate(RuleCategory.TIMEOUT, "self_test_delegate_probe")
        record = de.delegate(ev_probe, DelegationStrategy.LOAD_BALANCED, "self_test_task")
        if record is None:
            check_results.append(CheckResult("delegation", False, HealthLevel.DEGRADED, "delegate() returned None"))
        else:
            de.unregister_delegate("_self_test_probe")
            check_results.append(CheckResult("delegation", True, detail=f"delegated to {record.to_delegate}"))
    except Exception as e:
        check_results.append(CheckResult("delegation", False, HealthLevel.CRITICAL, str(e)))

    # Check 7: Active escalation count
    try:
        active = engine.get_active_count()
        check_results.append(CheckResult("active_count", True, detail=f"{active} active"))
    except Exception as e:
        check_results.append(CheckResult("active_count", False, HealthLevel.DEGRADED, str(e)))

    # Check 8: Extension detectors (optional — degraded if missing)
    try:
        from zephyr.governance.escalation.escalation_engine import EscalationEngine as EE

        engine_with_hooks = EE("self-test-hooks", hooks_enabled=True)
        detector_count = len(engine_with_hooks._extension_detectors)
        if detector_count == 0:
            check_results.append(
                CheckResult("extensions", False, HealthLevel.DEGRADED, "No extension detectors loaded")
            )
        else:
            check_results.append(CheckResult("extensions", True, detail=f"{detector_count} detectors"))
    except Exception as e:
        check_results.append(CheckResult("extensions", False, HealthLevel.DEGRADED, str(e)))

    report.checks = check_results
    report.total_passed = sum(1 for c in check_results if c.passed)
    report.total_failed = sum(1 for c in check_results if not c.passed)
    critical_failures = [c for c in check_results if not c.passed and c.level is HealthLevel.CRITICAL]
    degraded_failures = [c for c in check_results if not c.passed and c.level is HealthLevel.DEGRADED]

    if critical_failures:
        report.overall = HealthLevel.CRITICAL
    elif degraded_failures:
        report.overall = HealthLevel.DEGRADED
    else:
        report.overall = HealthLevel.HEALTHY

    report.duration_ms = (time.perf_counter() - t0) * 1000
    return report


def main():
    warn_only = "--warn-only" in sys.argv
    json_flag = "--json" in sys.argv

    report = run_self_test()

    if json_flag:
        output = {
            "overall": report.overall.value,
            "total_passed": report.total_passed,
            "total_failed": report.total_failed,
            "duration_ms": round(report.duration_ms, 2),
            "checks": [
                {"name": c.name, "passed": c.passed, "level": c.level.value, "detail": c.detail} for c in report.checks
            ],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("Escalation Protocol Self-Test — MOD-INF-022")
        print(f"  Result: {report.overall.value.upper()}")
        print(f"  Passed: {report.total_passed}/{len(report.checks)} ({report.duration_ms:.1f}ms)")
        print()
        for c in report.checks:
            icon = "✓" if c.passed else "✗"
            print(f"  {icon} {c.name}: {c.detail}")

    if report.overall is HealthLevel.CRITICAL:
        return 2
    if report.overall is HealthLevel.DEGRADED:
        return 0 if warn_only else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
