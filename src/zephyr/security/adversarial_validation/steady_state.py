# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.steady_state
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py; game_day_runner.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 35 metrics across 6 domains: compliance(6)/security(5)/performance(5)/risk(5)/operations(5)/resilience(5); drift threshold 5% per metric
# [MODIFY-GUARD] Adding metrics MUST update DOMAIN_METRICS and SteadyStateSummary model
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SteadyStateDriftError if drift_rate > 50% after attack
# [TESTS] tests/red_blue/test_steady_state.py
# [A_module] module_id=MOD-SEC_steady_state | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import subprocess
import time
from pathlib import Path

from zephyr.security.adversarial_validation.models import SteadyStateSummary

logger = logging.getLogger(__name__)

__all__: list[str] = ["SteadyState", "SteadyStateDriftError"]

DOMAIN_METRICS: Final[dict[str, list[dict]]] = {
    "compliance": [
        {"metric": "rule_coverage", "check": "grep_count:project_rules.md:RULE-", "baseline": 9},
        {"metric": "registry_completeness", "check": "grep_count:_registry.yaml:module_id", "baseline": 30},
        {"metric": "gate_count", "check": "grep_count:gates/_registry.yaml:gate_id", "baseline": 46},
        {"metric": "audit_pass_rate", "check": "script:audit_registration.py:exit_code", "baseline": 0},
        {"metric": "lock_clean_count", "check": "dir_count:.ailocks:", "baseline": 0},
        {"metric": "contract_freeze_count", "check": "grep_count:contract_registry.py:frozen", "baseline": 0},
    ],
    "security": [
        {"metric": "secret_leak_count", "check": "script:scan_secret_leak.py:exit_code", "baseline": 0},
        {"metric": "rbac_violations", "check": "grep_count:agent_rbac:violation", "baseline": 0},
        {"metric": "injection_attempts", "check": "grep_count:llm_security:injection", "baseline": 0},
        {"metric": "immutable_core_modifications", "check": "grep_count:immutable_core:MODIFIED", "baseline": 0},
        {"metric": "escalation_pending", "check": "grep_count:escalation_engine:PENDING", "baseline": 0},
    ],
    "performance": [
        {"metric": "script_count", "check": "dir_count:scripts/governance:", "baseline": 268},
        {"metric": "test_pass_rate", "check": "script:pytest --collect-only:exit_code", "baseline": 0},
        {"metric": "import_time_ms", "check": "import_time:zephyr.security.adversarial_validation", "baseline": 500},
        {"metric": "db_size_kb", "check": "file_size:data/databases/governance.db", "baseline": 2048},
        {"metric": "lock_acquisition_ms", "check": "lock_time:models.py", "baseline": 100},
    ],
    "risk": [
        {"metric": "circuit_breaker_trips", "check": "grep_count:escalation_engine:CIRCUIT_OPEN", "baseline": 0},
        {"metric": "deadlock_events", "check": "grep_count:escalation_engine:DEADLOCK", "baseline": 0},
        {"metric": "budget_exceeded", "check": "grep_count:budget_enforcer:EXCEEDED", "baseline": 0},
        {"metric": "drift_events", "check": "grep_count:drift_detector:DRIFT", "baseline": 0},
        {"metric": "orphan_count", "check": "script:audit_registration.py:orphan_count", "baseline": 9},
    ],
    "operations": [
        {"metric": "session_count", "check": "dir_count:session_logs:", "baseline": 10},
        {"metric": "temp_file_count", "check": "glob_count:_temp*.py", "baseline": 0},
        {"metric": "backup_count", "check": "dir_count:data/red_blue/backups:", "baseline": 0},
        {"metric": "log_size_kb", "check": "file_size:logs/", "baseline": 1024},
        {"metric": "mcp_up_count", "check": "process_count:mcp_server", "baseline": 7},
    ],
    "resilience": [
        {"metric": "kill_switch_active", "check": "grep_count:kill_switch.py:ACTIVE", "baseline": 0},
        {"metric": "auto_recovery_count", "check": "grep_count:escalation_engine:AUTO_RECOVERY", "baseline": 0},
        {"metric": "retry_count", "check": "grep_count:task_repo.py:RETRY", "baseline": 0},
        {"metric": "degraded_services", "check": "grep_count:orchestrator:DEGRADED", "baseline": 0},
        {"metric": "rollback_count", "check": "grep_count:rollback.py:ROLLBACK", "baseline": 0},
    ],
}


class SteadyStateDriftError(RuntimeError):
    pass


class SteadyState:
    def __init__(self) -> None:
        self._snapshot_before: dict[str, dict[str, float]] = {}
        self._snapshot_after: dict[str, dict[str, float]] = {}

    def verify_before_attack(self) -> dict[str, dict[str, float]]:
        self._snapshot_before = self._measure_all()
        logger.info("steady_state_before metrics=%d", len(self._snapshot_before))
        return self._snapshot_before

    def verify_after_attack(self) -> SteadyStateSummary:
        self._snapshot_after = self._measure_all()
        summary = self._compute_drift()
        if summary.drift_rate > 50.0:
            raise SteadyStateDriftError(
                f"Steady state severely drifted: {summary.drifted}/{summary.total_metrics} metrics outside threshold"
            )
        logger.info("steady_state_after drifted=%d total=%d", summary.drifted, summary.total_metrics)
        return summary

    def _measure_all(self) -> dict[str, dict[str, float]]:
        results: dict[str, dict[str, float]] = {}
        for domain, metrics in DOMAIN_METRICS.items():
            results[domain] = {}
            for m in metrics:
                results[domain][m["metric"]] = self._evaluate_metric(m)
        return results

    def _evaluate_metric(self, metric_def: dict) -> float:
        check = metric_def["check"]
        try:
            if check.startswith("grep_count:"):
                return self._grep_count(check[11:])
            elif check.startswith("dir_count:"):
                return self._dir_count(check[10:])
            elif check.startswith("file_size:"):
                return self._file_size_kb(check[10:])
            elif check.startswith("script:"):
                return self._script_exit_code(check[7:])
            elif check.startswith("import_time:"):
                return self._import_time(check[12:])
            elif check.startswith("lock_time:"):
                return self._lock_time(check[10:])
            elif check.startswith("glob_count:"):
                return self._glob_count(check[11:])
            elif check.startswith("process_count:"):
                return self._process_count(check[14:])
        except Exception:
            logger.exception("metric_eval_failed metric=%s", metric_def["metric"], exc_info=True)
        return -1.0

    def _grep_count(self, spec: str) -> float:
        parts = spec.split(":", 2)
        file_pattern, pattern = parts[0], parts[1] if len(parts) > 1 else ""
        src = Path("src/zephyr") / file_pattern if not file_pattern.startswith("src/") else Path(file_pattern)
        if not src.exists():
            return 0.0
        try:
            result = subprocess.run(
                ["grep", "-r", "-c", pattern, str(src)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            total = sum(int(line.split(":")[-1]) for line in result.stdout.strip().split("\n") if ":" in line)
            return float(total)
        except Exception:
            return 0.0

    def _dir_count(self, path_str: str) -> float:
        p = Path(path_str.rstrip(":"))
        if not p.exists():
            return 0.0
        return float(len(list(p.iterdir())))

    def _file_size_kb(self, path_str: str) -> float:
        p = Path(path_str.rstrip(":"))
        if not p.exists():
            return 0.0
        return round(p.stat().st_size / 1024.0, 1)

    def _script_exit_code(self, spec: str) -> float:
        parts = spec.split(":", 1)
        script, field = parts[0], parts[1] if len(parts) > 1 else "exit_code"
        full_path = Path("scripts/governance") / script if not script.startswith("scripts/") else Path(script)
        if not full_path.exists():
            return -1.0
        try:
            result = subprocess.run(
                ["python", str(full_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return float(result.returncode)
        except Exception:
            return -1.0

    def _import_time(self, module: str) -> float:
        try:
            start = time.perf_counter()
            __import__(module)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return round(elapsed_ms, 1)
        except Exception:
            logger.warning("import_time_failed module=%s", module, exc_info=True)
            return -1.0

    def _lock_time(self, file_path: str) -> float:
        try:
            start = time.perf_counter()
            result = subprocess.run(
                ["python", "scripts/lock_files.py", "check", file_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            if result.returncode == 0:
                return round(elapsed_ms, 1)
            logger.warning("lock_time_check_failed file=%s rc=%d", file_path, result.returncode)
            return round(elapsed_ms, 1)
        except Exception:
            logger.warning("lock_time_failed file=%s", file_path, exc_info=True)
            return -1.0

    def _glob_count(self, pattern: str) -> float:
        count = len(list(Path().glob(pattern)))
        return float(count)

    def _process_count(self, name: str) -> float:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return float(result.stdout.count(name))
        except Exception:
            return 0.0

    def _compute_drift(self) -> SteadyStateSummary:
        total = 0
        within = 0
        drifted = 0
        for domain, after_metrics in self._snapshot_after.items():
            before_metrics = self._snapshot_before.get(domain, {})
            for metric_name, after_val in after_metrics.items():
                total += 1
                before_val = before_metrics.get(metric_name, after_val)
                if before_val == 0:
                    if after_val == 0:
                        within += 1
                    else:
                        drifted += 1
                else:
                    pct_change = abs(after_val - before_val) / abs(before_val) * 100
                    if pct_change <= 5.0:
                        within += 1
                    else:
                        drifted += 1

        drift_rate = round(drifted / total * 100, 1) if total > 0 else 0.0
        return SteadyStateSummary(
            total_metrics=total,
            within_threshold=within,
            drifted=drifted,
            drift_rate=drift_rate,
        )