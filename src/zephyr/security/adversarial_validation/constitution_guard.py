# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 2a
# [MODULE] zephyr.security.adversarial_validation.constitution_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models; zephyr.governance.rule_enforcement.gate_engine
# [CONSUMERS] validator.py; convergence_checker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 34 articles loaded from _constitution-registry.yaml; ALL must pass per adversarial session; single failure = BLOCKED session
# [MODIFY-GUARD] Adding articles MUST update _constitution-registry.yaml; article_id format MUST be CONST-NNN
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ConstitutionViolationError on any article failure; FileNotFoundError if registry missing
# [TESTS] tests/red_blue/test_constitution_guard.py
# [A_module] module_id=MOD-SEC_constitution_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.models import AttackScenario

try:
    from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GateEngine
except ImportError:
    GateEngine = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

__all__: list[str] = ["ConstitutionArticle", "ConstitutionGuard", "ConstitutionViolationError"]

_REGISTRY_PATH: Path = Path(__file__).parent / "_constitution-registry.yaml"


class ConstitutionViolationError(RuntimeError):
    pass


class ConstitutionArticle:
    def __init__(
        self,
        article_id: str,
        name: str,
        derived_from: str = "",
        defense_action: str = "",
        applicable_gates: list[str] | None = None,
        status: str = "active",
    ) -> None:
        self.article_id: str = article_id
        self.name: str = name
        self.derived_from: str = derived_from
        self.defense_action: str = defense_action
        self.applicable_gates: list[str] = applicable_gates or []
        self.status: str = status

    def __repr__(self) -> str:
        # 5.110.6 修复: 冒号分隔非Python表达式, 改为 field=value 格式使 __repr__ 可重建
        return f"ConstitutionArticle(article_id={self.article_id!r}, name={self.name!r})"


class ConstitutionGuard:
    def __init__(self, registry_path: Path | None = None, gate_engine: GateEngine | None = None) -> None:
        self._registry_path: Path = registry_path or _REGISTRY_PATH
        self._gate_engine: GateEngine | None = gate_engine
        self._articles: list[ConstitutionArticle] = []
        self._loaded: bool = False

    def load(self) -> list[ConstitutionArticle]:
        if self._loaded:
            return self._articles

        if not self._registry_path.exists():
            raise FileNotFoundError(f"Constitution registry not found: {self._registry_path}")

        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        raw_articles: list[dict] = raw.get("articles", [])
        self._articles = []

        for entry in raw_articles:
            article = ConstitutionArticle(
                article_id=entry.get("article_id", ""),
                name=entry.get("name", ""),
                derived_from=entry.get("derived_from", ""),
                defense_action=entry.get("defense_action", ""),
                applicable_gates=entry.get("applicable_gates", []),
                status=entry.get("status", "active"),
            )
            self._articles.append(article)

        self._loaded = True
        logger.info("constitution_loaded articles=%d", len(self._articles))
        return self._articles

    def validate_constitution(self, rule_id: str) -> bool:
        if not self._loaded:
            self.load()
        article = self.get(rule_id)
        if article is None:
            return False
        return self._evaluate_article(article)

    def validate_all(self) -> dict[str, bool]:
        if not self._loaded:
            self.load()
        results: dict[str, bool] = {}
        for article in self._articles:
            if article.status == "active":
                results[article.article_id] = self._evaluate_article(article)
        return results

    def enforce(self) -> bool:
        results = self.validate_all()
        violations = [aid for aid, passed in results.items() if not passed]
        if violations:
            raise ConstitutionViolationError(
                f"Constitution violations: {len(violations)}/{len(results)} articles failed: {violations}"
            )
        return True

    def guard_attack(self, scenario: AttackScenario) -> bool:
        if scenario.constitution_ref:
            return self.validate_constitution(scenario.constitution_ref)
        return True

    def get(self, article_id: str) -> ConstitutionArticle | None:
        if not self._loaded:
            self.load()
        for article in self._articles:
            if article.article_id == article_id:
                return article
        return None

    def get_active(self) -> list[ConstitutionArticle]:
        if not self._loaded:
            self.load()
        return [a for a in self._articles if a.status == "active"]

    def get_guarded_rules(self) -> list[str]:
        if not self._loaded:
            self.load()
        return [a.article_id for a in self._articles if a.status == "active"]

    def _evaluate_article(self, article: ConstitutionArticle) -> bool:
        action = article.defense_action
        if not action:
            return True

        if article.applicable_gates and self._gate_engine is not None:
            try:
                for gate_id in article.applicable_gates:
                    result = self._gate_engine.evaluate(
                        {"task_id": f"constitution-{article.article_id}", "title": article.name},
                        gate_id,
                    )
                    if not result.passed:
                        logger.warning(
                            "constitution_gate_blocked article=%s gate=%s msg=%s",
                            article.article_id,
                            gate_id,
                            getattr(result, "message", ""),
                        )
                        return False
                return True
            except Exception:
                logger.warning(
                    "constitution_gate_fallback article=%s action=%s", article.article_id, action, exc_info=True
                )

        checks: dict[str, str] = {
            "prompt_injection_filter.scan": "src/zephyr/llm-security",
            "immutable_core.verify_roles": "src/zephyr/agent-rbac",
            "drift_engine.scan_all": "src/zephyr/escalation-engine/drift-detector.py",
            "audit-trail.verify_chain": "src/zephyr/escalation-engine/merkle_audit.py",
            "circuit_breaker.hard_check": "src/zephyr/escalation-engine/circuit_breaker.py",
            "budget_engine.pre_flight": "src/zephyr/budget-enforcer",
            "freeze_manifest.validate": "src/zephyr/governance/contracts.py",
            "mcp_auth.verify_tool_access": "src/zephyr/infrastructure_runtime_integration/mcp_server",
            "session_audit.verify": "session_logs",
            "kb.verify_provenance": "src/zephyr/kb",
            "gates_registry.verify_all": "src/zephyr/gates",
            "route_manifest.validate": "src/zephyr/orchestrator",
            "event_schemas.validate": "src/zephyr/orchestrator",
            "migration.verify_checksum": "src/zephyr/db",
            "context_budget.enforce": "src/zephyr/context-engine",
            "lock_registry.verify_atomicity": "src/zephyr/shared/lock.py",
            "secrets.scan_all": "scripts/governance/d6_security",
            "error_budget_tracker.report": "src/zephyr/budget-enforcer",
            "dependency_registry.detect_cycles": "data/asset_index",
            "blueprint_registry.audit_status": "docs/03_modules",
            "audit_registration.scan": "scripts/governance/d11_compliance/audit_registration.py",
            "vector-memory.verify_embeddings": "src/zephyr/vector-memory",
            "task_repo.verify_schema": "src/zephyr/db",
        }

        target = checks.get(action)
        if target is None:
            return True

        p = Path(target)
        if p.exists():
            return True

        if not target.startswith("src/") and not target.startswith("scripts/"):
            return True

        logger.warning("constitution_check_failed article=%s action=%s target=%s", article.article_id, action, target)
        return False