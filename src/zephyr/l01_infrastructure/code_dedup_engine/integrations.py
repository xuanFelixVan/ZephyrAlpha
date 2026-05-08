"""集成管理——预提交钩子+CI-only 扫描+超时边界."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationConfig:
    precommit_enabled: bool = True
    ci_enabled: bool = True
    ci_cron: str = "0 3 * * *"
    precommit_timeout_ms: int = 5000
    ci_timeout_ms: int = 300000
    precommit_strategy: str = "MINHASH"
    ci_strategy: str = "AST_FUZZY"
    auto_register_precommit: bool = True


@dataclass
class IntegrationManager:
    config: IntegrationConfig = field(default_factory=IntegrationConfig)
    hooks: list[dict[str, Any]] = field(default_factory=list)

    def register_precommit(self) -> dict[str, Any]:
        return {
            "hook": "verify_dedup",
            "script": "scripts/pre-commit/verify_dedup.py",
            "strategy": self.config.precommit_strategy,
            "timeout_ms": self.config.precommit_timeout_ms,
            "enabled": self.config.precommit_enabled,
        }

    def register_ci(self) -> dict[str, Any]:
        return {
            "workflow": "dedup-test",
            "cron": self.config.ci_cron,
            "strategy": self.config.ci_strategy,
            "timeout_ms": self.config.ci_timeout_ms,
            "enabled": self.config.ci_enabled,
        }

    def status(self) -> dict[str, Any]:
        return {"precommit": self.register_precommit(), "ci": self.register_ci()}
