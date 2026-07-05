# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 2a
# [MODULE] zephyr.security.adversarial_validation.constitution_engine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] constitution_guard.py; bypass_recorder.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] New articles auto-generated from bypass patterns; article_id auto-assigned CONST-NNN; registry written with atomic os.replace
# [MODIFY-GUARD] Template categories: security_boundary/data_sovereignty/transaction_integrity/audit_immutability/agent_safety/knowledge_safety
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RegistryWriteError on failed atomic write; DuplicateArticleError on same derived_from
# [TESTS] tests/red_blue/test_constitution_engine.py
# [A_module] module_id=MOD-SEC_constitution_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.models import BypassEntry

logger = logging.getLogger(__name__)

__all__: list[str] = ["ConstitutionEngine", "DuplicateArticleError", "RegistryWriteError"]

_REGISTRY_PATH: Path = Path(__file__).parent / "_constitution-registry.yaml"

ARTICLE_CATEGORIES: dict[str, str] = {
    "security_boundary": "Security Boundary",
    "data_sovereignty": "Data Sovereignty",
    "transaction_integrity": "Transaction Integrity",
    "audit_immutability": "Audit Immutability",
    "agent_safety": "Agent Safety",
    "knowledge_safety": "Knowledge Safety",
}

TEMPLATES: dict[str, dict] = {
    "security_boundary": {
        "name": "No {vector} Bypass",
        "derived_from": "OWASP LLM01:2025",
        "defense_action": "{defense}.scan",
    },
    "data_sovereignty": {
        "name": "Data Integrity for {vector}",
        "derived_from": "GDPR Art.5(1)(d)",
        "defense_action": "{defense}.verify",
    },
    "transaction_integrity": {
        "name": "Atomicity for {vector}",
        "derived_from": "ACID Compliance",
        "defense_action": "{defense}.validate",
    },
    "audit_immutability": {
        "name": "Immutability for {vector}",
        "derived_from": "SOC2 CC6.1",
        "defense_action": "{defense}.verify_chain",
    },
    "agent_safety": {
        "name": "Agent Safety: {vector}",
        "derived_from": "MCP Security Best Practice",
        "defense_action": "{defense}.verify_tool_access",
    },
    "knowledge_safety": {
        "name": "KB Integrity: {vector}",
        "derived_from": " KB Integrity",
        "defense_action": "{defense}.verify_provenance",
    },
}


class RegistryWriteError(RuntimeError):
    pass


class DuplicateArticleError(RuntimeError):
    pass


class ConstitutionEngine:
    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path: Path = registry_path or _REGISTRY_PATH

    def learn_from_bypass(self, bypass: BypassEntry, target_module: str = "") -> str | None:
        if bypass.count < 3:
            return None

        existing = self._find_by_action(bypass.gate_id)
        if existing:
            logger.info("article_already_exists gate=%s article=%s", bypass.gate_id, existing)
            return None

        category = self._classify(bypass.root_cause)
        article_id = self._next_article_id()
        template = TEMPLATES[category]

        name = template["name"].format(vector=bypass.gate_id, defense=bypass.gate_id)
        defense_action = template["defense_action"].format(defense=bypass.gate_id, defense_action=bypass.gate_id)

        new_article = {
            "article_id": article_id,
            "name": name,
            "derived_from": template["derived_from"],
            "defense_action": defense_action,
            "applicable_gates": [bypass.gate_id],
            "status": "active",
            "category": category,
            "generated_from": bypass.entry_id,
        }

        self._append_to_registry(new_article)
        logger.info("article_generated article_id=%s name=%s category=%s", article_id, name, category)
        return article_id

    def _classify(self, root_cause: str) -> str:
        keywords: dict[str, str] = {
            "injection": "security_boundary",
            "prompt": "security_boundary",
            "bypass": "security_boundary",
            "data": "data_sovereignty",
            "privacy": "data_sovereignty",
            "atomic": "transaction_integrity",
            "transaction": "transaction_integrity",
            "audit": "audit_immutability",
            "log": "audit_immutability",
            "immutable": "audit_immutability",
            "agent": "agent_safety",
            "mcp": "agent_safety",
            "tool": "agent_safety",
            "knowledge": "knowledge_safety",
            "kb": "knowledge_safety",
            "provenance": "knowledge_safety",
        }
        rc_lower = root_cause.lower()
        for keyword, category in keywords.items():
            if keyword in rc_lower:
                return category
        return "security_boundary"

    def _next_article_id(self) -> str:
        if not self._registry_path.exists():
            return "CONST-001"
        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        articles = raw.get("articles", [])
        max_id = 0
        for a in articles:
            aid = a.get("article_id", "")
            if aid.startswith("CONST-"):
                try:
                    num = int(aid.split("-")[1])
                    if num > max_id:
                        max_id = num
                except ValueError:
                    pass
        return f"CONST-{max_id + 1:03d}"

    def _find_by_action(self, defense_action: str) -> str | None:
        if not self._registry_path.exists():
            return None
        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for article in raw.get("articles", []):
            if article.get("defense_action") == defense_action:
                return article.get("article_id")
        return None

    def _append_to_registry(self, article: dict) -> None:
        if not self._registry_path.exists():
            raise RegistryWriteError(f"Registry not found: {self._registry_path}")

        with open(self._registry_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        articles: list[dict] = raw.get("articles", [])
        articles.append(article)
        raw["articles"] = articles
        raw["total_articles"] = len(articles)
        from datetime import UTC, datetime

        raw["last_updated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        tmp = self._registry_path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(raw, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, self._registry_path)
