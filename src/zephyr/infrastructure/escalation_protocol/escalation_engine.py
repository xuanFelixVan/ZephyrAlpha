"""
Escalation Engine — MOD-INF-022 v0.14.0 backward-compatible wrapper.

⚠ DEPRECATED: This module is a backward-compat shim for code that imports from
   `zephyr.infrastructure.escalation_protocol.escalation_engine`.
   All new code MUST import from `zephyr.escalation` instead.

   from zephyr.escalation import EscalationEngine, EscalationLevel, RuleCategory  # ← correct

This wrapper maps the old API (autonomous/auto_guard/blocked) to the new
L0-L4 escalation model with CircuitBreaker + EconomicGuard + DelegationEngine.

Blueprint: docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md §2
"""

from __future__ import annotations

import warnings
from enum import Enum

import yaml

warnings.warn(
    "zephyr.infrastructure.escalation_protocol.escalation_engine is DEPRECATED. "
    "Use `from zephyr.escalation import EscalationEngine` instead.",
    DeprecationWarning,
    stacklevel=2,
)


class EscalationLevel(str, Enum):
    AUTONOMOUS = "autonomous"
    AUTO_GUARD = "auto_guard"
    BLOCKED = "blocked"


class Rule:
    def __init__(self, rule_id, level, priority, patterns, window_sec=300):
        self.rule_id = rule_id
        self.level = EscalationLevel(level)
        self.priority = priority
        self.patterns = patterns
        self.window_sec = window_sec


_LEVEL_MAP = {
    "autonomous": "autonomous",
    "auto_guard": "auto_guard",
    "blocked": "blocked",
}


class EscalationEngine:
    def __init__(self, rules_path=None):
        self._rules_path = rules_path or "src/zephyr/infrastructure/escalation_protocol/escalation_rules.yaml"
        self._rules: list[Rule] = []
        self._trigger_cache: dict[str, list[float]] = {}
        self._notified: set[str] = set()
        self.deny_by_default = True
        self._load_rules()

        try:
            from zephyr.escalation_engine.escalation_engine import EscalationEngine as _NewEngine
            from zephyr.escalation_engine.escalation_models import RuleCategory as _RC

            self._new_engine = _NewEngine("legacy-shim")
            self._new_available = True
        except ImportError:
            self._new_engine = None
            self._new_available = False

    def _load_rules(self):
        try:
            with open(self._rules_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
        new_default_rules = [
            ("ESC-001", "blocked", 100, ["rm -rf", "format", "DROP TABLE", "destroy"]),
            ("ESC-002", "blocked", 90, ["git push --force", "overwrite_production", "force_push"]),
            ("ESC-003", "blocked", 85, ["delete_from_database", "purge_logs", "truncate"]),
            ("ESC-004", "blocked", 80, ["modify_blueprint", "modify_architecture_yaml", "rewrite_spec"]),
            ("ESC-005", "blocked", 75, ["expose_secret", "print_env", "log_credential"]),
            ("ESC-006", "blocked", 70, ["kill_process", "shutdown_service", "terminate"]),
            ("ESC-007", "blocked", 60, ["modify_shared_module", "modify_schemas", "change_contract"]),
            ("ESC-008", "blocked", 50, ["write_outside_project", "access_network_external", "outbound_connection"]),
            ("ESC-009", "auto_guard", 40, ["run_expensive_query", "large_file_write", "bulk_operation"]),
            ("ESC-010", "auto_guard", 30, ["unfamiliar_directory", "unknown_command", "experimental"]),
        ]
        rules_data = data.get("rules", new_default_rules)
        for entry in rules_data:
            if isinstance(entry, dict):
                self._rules.append(
                    Rule(
                        rule_id=entry["rule_id"],
                        level=entry["level"],
                        priority=entry["priority"],
                        patterns=entry["patterns"],
                        window_sec=entry.get("window_sec", 300),
                    )
                )
            else:
                self._rules.append(Rule(*entry))

    def evaluate(self, operation: str) -> EscalationLevel:
        import time

        now = time.time()
        matched_rules = []
        for rule in self._rules:
            for pattern in rule.patterns:
                if pattern.lower() in operation.lower() or pattern.replace("_", " ") in operation.lower():
                    matched_rules.append(rule)
                    break
        if not matched_rules:
            result = EscalationLevel.BLOCKED if self.deny_by_default else EscalationLevel.AUTONOMOUS
        else:
            matched_rules.sort(key=lambda r: r.priority, reverse=True)
            winner = matched_rules[0]
            for rule in matched_rules:
                key = f"{operation}:{rule.rule_id}"
                self._trigger_cache.setdefault(key, []).append(now)
                self._trigger_cache[key] = [t for t in self._trigger_cache[key] if now - t < rule.window_sec]
            self._notified.add(f"{operation}:{winner.rule_id}")
            result = winner.level

        if self._new_available and result == EscalationLevel.BLOCKED:
            try:
                from zephyr.escalation_engine.escalation_models import RuleCategory

                ev = self._new_engine.evaluate(RuleCategory.SECURITY_VIOLATION, operation)
                if ev.circuit_breaker_triggered:
                    return EscalationLevel.BLOCKED
            except Exception:
                pass

        return result

    def get_match_details(self, operation: str) -> dict:
        matched = []
        for rule in self._rules:
            for pattern in rule.patterns:
                if pattern.lower() in operation.lower():
                    matched.append(
                        {
                            "rule_id": rule.rule_id,
                            "level": rule.level.value,
                            "priority": rule.priority,
                            "pattern": pattern,
                        }
                    )
                    break
        return {"operation": operation, "matched_rules": matched, "count": len(matched)}
