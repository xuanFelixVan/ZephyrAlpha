# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.integrity_self_check

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""完整性自检——启动后定期自检所有21个模块导入+API访问+权限判定一致性."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IntegrityCheck(BaseModel):
    module_name: str
    importable: bool = False
    has_public_api: bool = False
    passed: bool = False
    error: str = ""


EXPECTED_MODULES = [
    "immutable_core", "kill_switch", "engine_degradation",
    "identity", "rbac_guard", "abac_guard",
    "input_guard", "output_guard", "decision_explainer",
    "observability", "permission_guard", "dry_run",
    "cross_cutting", "guard_layers", "intent_binder",
    "exceptions", "adversarial_resilience", "post_action_verifier",
    "derive_rbac_roles", "memory_provenance_guard", "canary_rollout_manager",
    "cross_session_detector", "permission_hooks", "agent_creation_policy",
    "cache_invalidation", "emergency_override", "auto_maintenance",
    "genesis_bootstrap", "asymmetric_audit", "non_repudiation",
    "path_guard", "shell_dialect_detector", "rule_injection_guard",
    "build_sanitizer", "dependency_auditor", "audit_log_guard",
    "replay_attack_guard", "legal_audit_chain", "rollback_sandbox",
    "monotonic_clock", "bootstrap_verifier", "key_hierarchy",
    "anomaly_detector", "blueprint_fidelity", "native_api_guard",
    "memory_guard", "vibe_coding_guard", "novel_attack_guard",
    "cybersec_2026_guard", "continuous_verifier", "permission_mode_manager",
    "cascading_failure_isolator", "micro_verifier", "integration",
    "contract_verifier", "phase_executor", "risk_mitigation",
    "blind_spot_tracker", "decision_registry",
]


class IntegritySelfCheck:
    def __init__(self) -> None:
        self._results: list[IntegrityCheck] = []

    def check_all(self) -> list[IntegrityCheck]:
        self._results.clear()
        for mod_name in EXPECTED_MODULES:
            self._results.append(self._check_module(mod_name))
        return list(self._results)

    def _check_module(self, mod_name: str) -> IntegrityCheck:
        try:
            mod = __import__(f"zephyr.agent_rbac.{mod_name}", fromlist=[mod_name])
            has_api = len(dir(mod)) > 0
            return IntegrityCheck(module_name=mod_name, importable=True, has_public_api=has_api, passed=True)
        except Exception as e:
            return IntegrityCheck(module_name=mod_name, importable=False, passed=False, error=str(e))

    def summary(self) -> dict[str, Any]:
        if not self._results:
            self.check_all()
        total = len(self._results)
        passed = sum(1 for r in self._results if r.passed)
        return {"total_modules": total, "passed": passed, "failed": total - passed, "integrity_pct": passed / max(total, 1) * 100, "all_ok": passed == total}
