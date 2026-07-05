# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.spec_engine
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.shared.contracts.protocols; zephyr.governance.audit_trail.writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — SpecEngine 蓝图→Skill 升级引擎
============================================================
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0

SpecEngine 是 agent-spec 的统一入口，负责将静态蓝图转化为可执行 Agent Skill。
四阶段流程: discover(发现) → generate(生成) → validate(验证) → register(注册)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from zephyr.autonomy_core.skills.skill_factory import SkillFactory
from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel
from zephyr.autonomy_core.skills.skill_loader import SkillLoader
from zephyr.autonomy_core.trigger_router import TriggerRouter

_AUDIT_AVAILABLE = False
try:
    from zephyr.governance.audit_trail.writer import AuditWriter
    from zephyr.shared.contracts.protocols import AuditWriterProtocol

    _AUDIT_AVAILABLE = True
except ImportError:
    AuditWriter = None


class UpgradePhase:
    DISCOVER = "discover"
    GENERATE = "generate"
    VALIDATE = "validate"
    REGISTER = "register"
    COMPLETE = "complete"
    FAILED = "failed"

    ORDERED = [DISCOVER, GENERATE, VALIDATE, REGISTER, COMPLETE]


class UpgradeResult:
    def __init__(self, blueprint_path: str):
        self.blueprint_path = blueprint_path
        self.phase = UpgradePhase.DISCOVER
        self.skill_id: str | None = None
        self.skill_path: Path | None = None
        self.module_name: str = ""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.phase_results: dict[str, dict[str, Any]] = {}
        self.started_at = datetime.now(UTC)
        self.finished_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_path": self.blueprint_path,
            "phase": self.phase,
            "skill_id": self.skill_id,
            "skill_path": str(self.skill_path) if self.skill_path else None,
            "module_name": self.module_name,
            "errors": self.errors,
            "warnings": self.warnings,
            "phase_results": self.phase_results,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "success": self.phase == UpgradePhase.COMPLETE,
        }


class SpecEngine:
    """蓝图→Skill 升级引擎 —— agent-spec 统一入口

    用法:
        engine = SpecEngine()
        result = engine.upgrade("docs/03_modules/_domain-infra_ops/db/blueprint.md")
        print(result.to_dict())
    """

    def __init__(self, registry_path: Path | None = None):
        self.factory = SkillFactory()
        self.loader = SkillLoader(registry_path)
        self.freshness = FreshnessDecayModel()
        self.router = TriggerRouter()
        self._audit_writer = AuditWriter() if _AUDIT_AVAILABLE else None

    def upgrade(self, blueprint_path: str) -> UpgradeResult:
        result = UpgradeResult(blueprint_path)

        try:
            result.module_name = self._discover(blueprint_path, result)
            if not result.module_name:
                return self._fail(result, "discover", "Could not determine module name from blueprint")

            skill_path = self._generate(result.module_name, blueprint_path, result)
            if skill_path is None:
                return self._fail(result, "generate", "Skill generation failed")

            result.skill_path = skill_path

            if not self._validate(result):
                return self._fail(result, "validate", "Skill validation failed")

            self._register(result)

            result.phase = UpgradePhase.COMPLETE
            result.finished_at = datetime.now(UTC)
            self._write_audit("skill_upgrade_complete", result)

        except Exception as exc:
            return self._fail(result, result.phase, str(exc))

        return result

    def upgrade_batch(self, blueprint_paths: list[str]) -> list[UpgradeResult]:
        results = []
        for bp in blueprint_paths:
            results.append(self.upgrade(bp))
        return results

    def status(self, skill_id: str | None = None) -> dict[str, Any]:
        if skill_id:
            return {
                "skill_id": skill_id,
                "freshness": self.freshness.current_state(skill_id),
                "registry": self._lookup_registry(skill_id),
            }
        registry = self.loader._load_registry()
        skills = registry.get("skills", {})
        return {
            "total_domain": len(skills.get("domain", {})),
            "total_role": len(skills.get("role", {})),
            "total": registry.get("metadata", {}).get("total_skills", 0),
            "active": registry.get("metadata", {}).get("active_skills", 0),
            "deprecated": registry.get("metadata", {}).get("deprecated_skills", 0),
        }

    def validate_skill(self, skill_id: str) -> dict[str, Any]:
        try:
            data = self.loader.progressive_load(skill_id)
            l1 = data.get("l1", {})
            freshness = l1.get("freshness_score", 0)
            return {
                "skill_id": skill_id,
                "valid": True,
                "has_l1": bool(l1),
                "has_l2": bool(data.get("l2")),
                "freshness_score": freshness,
                "freshness_ok": freshness >= 30.0,
                "l3_count": len(data.get("l3_available", [])),
            }
        except Exception as exc:
            return {"skill_id": skill_id, "valid": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # 四阶段内部方法
    # ------------------------------------------------------------------

    def _discover(self, blueprint_path: str, result: UpgradeResult) -> str:
        result.phase = UpgradePhase.DISCOVER
        bp = Path(blueprint_path)
        if not bp.exists():
            result.errors.append(f"Blueprint not found: {blueprint_path}")
            return ""

        content = bp.read_text(encoding="utf-8")

        fm_match = yaml.safe_load(content.split("---\n")[1]) if "---" in content else {}
        module_name = fm_match.get("title", "").strip() if fm_match else ""

        if not module_name:
            for line in content.split("\n"):
                if line.startswith("# ") and "蓝图" in line:
                    module_name = line.lstrip("# ").strip()
                    break

        if not module_name:
            try:
                parts = bp.parent.parts
                for p in parts:
                    if p not in ("docs", "03_modules", "infra_ops"):
                        module_name = p
                        break
            except Exception as e:
                logger.warning("suppressed error in spec_engine", exc_info=True)

        result.phase_results["discover"] = {"module_name": module_name, "blueprint": blueprint_path}
        return module_name

    def _generate(self, module_name: str, blueprint_path: str, result: UpgradeResult) -> Path | None:
        result.phase = UpgradePhase.GENERATE
        try:
            skill_path = self.factory.generate_domain_skill(module_name, blueprint_path)
            result.phase_results["generate"] = {"skill_path": str(skill_path)}
            return skill_path
        except Exception as exc:
            result.errors.append(f"Generation error: {exc}")
            result.phase_results["generate"] = {"error": str(exc)}
            return None

    def _validate(self, result: UpgradeResult) -> bool:
        result.phase = UpgradePhase.VALIDATE
        valid = True

        if result.skill_path and not result.skill_path.exists():
            result.errors.append(f"Generated skill file missing: {result.skill_path}")
            valid = False

        registry = self.loader._load_registry()
        skills = registry.get("skills", {}).get("domain", {})
        for sid, data in skills.items():
            if data.get("name") == result.module_name:
                result.skill_id = sid
                break

        if result.skill_id:
            try:
                skill_data = self.loader.progressive_load(result.skill_id)
                l1 = skill_data.get("l1", {})
                if not l1.get("skill_id"):
                    result.warnings.append("Generated skill has empty frontmatter skill_id")
                l2 = skill_data.get("l2", "")
                if not l2 or len(l2) < 50:
                    result.warnings.append("Generated skill body is too short — may be template placeholder")
            except Exception as exc:
                result.errors.append(f"Validation load error: {exc}")
                valid = False
        else:
            result.warnings.append("Skill not found in registry after generation")

        result.phase_results["validate"] = {"valid": valid, "skill_id": result.skill_id}
        return valid

    def _register(self, result: UpgradeResult):
        result.phase = UpgradePhase.REGISTER
        if result.skill_id:
            self.freshness.boost(result.skill_id, 100.0)
            result.phase_results["register"] = {
                "skill_id": result.skill_id,
                "freshness_boosted": True,
            }
        self._write_audit("skill_registered", result)

    def _fail(self, result: UpgradeResult, phase: str, reason: str) -> UpgradeResult:
        result.phase = UpgradePhase.FAILED
        result.errors.append(f"[{phase}] {reason}")
        result.finished_at = datetime.now(UTC)
        self._write_audit("skill_upgrade_failed", result)
        return result

    def _lookup_registry(self, skill_id: str) -> dict[str, Any] | None:
        registry = self.loader._load_registry()
        for category in ("domain", "role"):
            if skill_id in registry.get("skills", {}).get(category, {}):
                return registry["skills"][category][skill_id]
        return None

    def _write_audit(self, event_type: str, result: UpgradeResult):
        if self._audit_writer is not None:
            try:
                self._audit_writer.write(
                    {
                        "event_type": event_type,
                        "module": "agent-spec.engine",
                        "blueprint_path": result.blueprint_path,
                        "skill_id": result.skill_id,
                        "phase": result.phase,
                        "success": result.phase == UpgradePhase.COMPLETE,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
            except Exception as e:
                logger.warning("suppressed error in spec_engine", exc_info=True)


__all__ = ["SpecEngine", "UpgradePhase", "UpgradeResult"]
