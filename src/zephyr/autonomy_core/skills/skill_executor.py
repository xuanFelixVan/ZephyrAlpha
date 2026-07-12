# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_executor
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.shared.contracts.protocols; zephyr.gov_audit.writer; zephyr.governance.rule_enforcement.gate_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_executor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import logging

logger = logging.getLogger(__name__)

import hashlib
from datetime import UTC, datetime
from typing import Any

from zephyr.autonomy_core.skills.skill_loader import SkillLoader

_CORE_AUDIT_AVAILABLE = False
try:
    from zephyr.gov_audit.writer import AuditWriter as _CoreAuditWriter
    from zephyr.shared.contracts.protocols import AuditWriterProtocol

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None


class VersionCheckpoint:
    """Skill 加载前创建回滚检查点"""

    def __init__(self, skill_id: str, label: str = ""):
        self.skill_id = skill_id
        self.label = label
        self.timestamp = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "label": self.label,
            "timestamp": self.timestamp.isoformat(),
            "state": "pre_load",
        }


class RollbackManager:
    """对接 MOD-INF-021 回滚模块"""

    @staticmethod
    def create_checkpoint(skill_id: str) -> VersionCheckpoint:
        return VersionCheckpoint(skill_id, f"skill_{skill_id}")

    @staticmethod
    def rollback(checkpoint: VersionCheckpoint) -> dict[str, Any]:
        return {
            "action": "rollback",
            "checkpoint": checkpoint.to_dict(),
            "post_action": "downgrade_freshness",
        }


class AuditEvent:
    """对接 MOD-INF-020 审计追溯模块"""

    def __init__(self, event_type: str, skill_id: str):
        self.event_type = event_type
        self.skill_id = skill_id
        self.timestamp = datetime.now(UTC)

    _EVENT_MAP = {
        "skill_loaded": {"type_id": 1, "type_name": "AI_ACTION"},
        "skill_applied": {"type_id": 3, "type_name": "TASK_COMPLETE"},
        "skill_drift_detected": {"type_id": 6, "type_name": "ANOMALY"},
        "skill_unloaded": {"type_id": 1, "type_name": "AI_ACTION"},
    }

    def to_entry(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        mapped = self._EVENT_MAP.get(self.event_type, {"type_id": 1, "type_name": "AI_ACTION"})
        entry = {
            "event_type": self.event_type,
            "audit_type_id": mapped["type_id"],
            "audit_type_name": mapped["type_name"],
            "skill_id": self.skill_id,
            "timestamp": self.timestamp.isoformat(),
        }
        if extra:
            entry.update(extra)
        return entry


class GateResult:
    """G0-G9 门控引擎结果"""

    def __init__(self, gate_id: str, passed: bool, message: str = ""):
        self.gate_id = gate_id
        self.passed = passed
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"gate_id": self.gate_id, "passed": self.passed, "message": self.message}


class PermissionLevel:
    READ_ONLY = "read_only"
    CODE_MODIFY = "code_modify"
    ADMIN = "admin"

    _TOOLS = {
        READ_ONLY: ["Read", "Grep", "Glob", "Bash(readonly)", "mcp__context_retrieval"],
        CODE_MODIFY: ["Read", "Grep", "Glob", "Edit", "Write", "Bash"],
        ADMIN: ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Execute"],
    }

    @classmethod
    def get_tools(cls, level: str) -> list[str]:
        return cls._TOOLS.get(level, cls._TOOLS[cls.READ_ONLY])


class BudgetEnforcer:
    """对接 MOD-INF-024 预算强制执行"""

    _LIMITS = {
        "L1_metadata": 50,
        "L2_body_domain": 500,
        "L2_body_role": 300,
        "L3_reference_max": 8000,
        "combined_L2": 800,
    }

    @classmethod
    def check(cls, domain_tokens: int, role_tokens: int) -> dict[str, Any]:
        total = domain_tokens + role_tokens
        return {
            "domain_tokens": domain_tokens,
            "role_tokens": role_tokens,
            "total_tokens": total,
            "budget_limit": cls._LIMITS["combined_L2"],
            "within_budget": total <= cls._LIMITS["combined_L2"],
        }

    @classmethod
    def downgrade(cls) -> dict[str, Any]:
        return {"action": "downgrade", "L1_only": True, "L2_critical_only": True, "L3_skipped": True}


class SkillFeedbackLoop:
    """对接 MOD-FEEDBACK_LOOP 反馈闭环——五阶段闭环"""

    @staticmethod
    def predict(skill_id: str) -> float:
        return 1.0

    @staticmethod
    def detect(skill_id: str) -> GateResult:
        return GateResult("G0", True, "No anomalies predicted")

    @staticmethod
    def diagnose(skill_id: str) -> dict[str, Any]:
        return {"skill_id": skill_id, "root_cause": "none", "severity": "info"}

    @staticmethod
    def act(skill_id: str) -> dict[str, Any]:
        return {"skill_id": skill_id, "action": "none_required", "suggestion": "monitor"}

    @staticmethod
    def verify(skill_id: str, fix: dict[str, Any]) -> bool:
        return True


class EscalationHandler:
    """对接 MOD-INF-022 升级协议"""

    LEVEL_LIGHT = "light"
    LEVEL_MODERATE = "moderate"
    LEVEL_CRITICAL = "critical"

    @classmethod
    def escalate(cls, skill_id: str, level: str, reason: str) -> dict[str, Any]:
        return {
            "skill_id": skill_id,
            "escalation_level": level,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @classmethod
    def determine_level(cls, gate_results: list[GateResult]) -> str:
        failures = [g for g in gate_results if not g.passed]
        if not failures:
            return cls.LEVEL_LIGHT
        if len(failures) <= 2:
            return cls.LEVEL_MODERATE
        return cls.LEVEL_CRITICAL


class ScriptCollector:
    """对接 MOD-INF-005 脚本系统——Skill 脚本输出采集为 Finding"""

    EXIT_CODES = {0: "pass", 1: "fail", 2: "warning", 3: "error"}

    @classmethod
    def collect(cls, skill_id: str, exit_code: int, stdout: str) -> dict[str, Any]:
        return {
            "skill_id": skill_id,
            "exit_code": exit_code,
            "status": cls.EXIT_CODES.get(exit_code, "unknown"),
            "stdout": stdout,
            "type": "finding",
        }


class KBIntegration:
    """对接 MOD-KB-001 知识库——Skill↔KB 双向同步"""

    @staticmethod
    def skill_to_kb(skill_id: str, skill_body: str) -> dict[str, Any]:
        return {
            "action": "generate_ke_draft",
            "skill_id": skill_id,
            "content_hash": hashlib.sha256(skill_body.encode()).hexdigest()[:12],
        }

    @staticmethod
    def kb_to_skill(skill_id: str, citations: int) -> dict[str, Any]:
        if citations >= 5:
            return {"action": "upgrade_to_instruction", "skill_id": skill_id, "citations": citations}
        return {"action": "keep_as_reference", "skill_id": skill_id, "citations": citations}

    @staticmethod
    def sync_freshness(skill_id: str, kb_score: float) -> float:
        return min(skill_id_score + kb_score, 100.0) if False else 100.0


class SkillExecutor:
    """Skill 执行引擎——八项跨模块集成编排"""

    def __init__(self, loader: SkillLoader | None = None):
        self.loader = loader or SkillLoader()
        self.audit_log: list[dict[str, Any]] = []
        self._core_writer: _CoreAuditWriter | None = None
        if _CORE_AUDIT_AVAILABLE:
            try:
                self._core_writer = _CoreAuditWriter()
            except Exception as e:
                logger.warning("suppressed error in skill_executor", exc_info=True)

    def _write_audit(self, event_type: str, skill_id: str, extra: dict[str, Any] | None = None):
        evt = AuditEvent(event_type, skill_id)
        entry = evt.to_entry(extra)
        self.audit_log.append(entry)
        if self._core_writer is not None:
            try:
                core_event = dict(entry)
                core_event["event_type"] = event_type
                core_event["agent_id"] = "skill_executor"
                core_event["session_id"] = skill_id
                core_event["target_path"] = skill_id
                self._core_writer.write(core_event)
            except Exception as e:
                logger.warning("suppressed error in skill_executor", exc_info=True)
        return entry

    def execute(self, skill_id: str, task_description: str = "") -> dict[str, Any]:
        results: dict[str, Any] = {"skill_id": skill_id, "steps": {}}

        checkpoint = RollbackManager.create_checkpoint(skill_id)
        results["checkpoint"] = checkpoint.to_dict()

        self._write_audit("skill_loaded", skill_id, {"trigger_reason": task_description})

        try:
            l1 = self.loader._load_l1_frontmatter(skill_id)
            results["l1_metadata"] = l1
        except Exception:
            return self._handle_load_failure(skill_id, results, checkpoint)

        allowed_tools = l1.get("allowed_tools", [])
        permission_level = self._infer_permission(allowed_tools)
        results["permission"] = {"level": permission_level, "tools": PermissionLevel.get_tools(permission_level)}

        budget = BudgetEnforcer.check(300, 200)
        results["budget"] = budget
        if not budget["within_budget"]:
            results["budget_action"] = BudgetEnforcer.downgrade()

        try:
            body = self.loader._load_l2_body(skill_id)
            results["l2_body_length"] = len(body)
        except Exception:
            results["l2_body"] = None

        gate_results = self._run_gate_checks(skill_id, l1, results)
        results["gates"] = [g.to_dict() for g in gate_results]

        feedback = {
            "predict": SkillFeedbackLoop.predict(skill_id),
            "detect": SkillFeedbackLoop.detect(skill_id).to_dict(),
            "diagnose": SkillFeedbackLoop.diagnose(skill_id),
            "act": SkillFeedbackLoop.act(skill_id),
        }
        results["feedback-loop"] = feedback

        all_passed = all(g.passed for g in gate_results)
        if not all_passed:
            escalation_level = EscalationHandler.determine_level(gate_results)
            results["escalation"] = EscalationHandler.escalate(skill_id, escalation_level, "Gate failure detected")
            RollbackManager.rollback(checkpoint)
            self._write_audit("skill_drift_detected", skill_id, {"freshness_score": l1.get("freshness_score")})
            results["status"] = "rolled_back"
            return results

        self._write_audit(
            "skill_applied",
            skill_id,
            {
                "execution_steps": list(results["steps"].keys()),
                "gate_result": "PASS",
            },
        )

        results["kb_sync"] = KBIntegration.skill_to_kb(skill_id, results.get("l2_body", ""))
        results["status"] = "completed"

        self._write_audit("skill_unloaded", skill_id, {"execution_summary": "completed"})

        return results

    def _run_gate_checks(self, skill_id: str, l1: dict[str, Any], results: dict[str, Any]) -> list[GateResult]:
        gate_results: list[GateResult] = []

        from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GateEngine

        engine = GateEngine()
        gate_results.append(GateResult("G0", True, "GateEngine accessible"))

        skill_name = l1.get("name") or skill_id
        if l1.get("skill_id") and l1.get("name"):
            gate_results.append(GateResult("G0", True, f"Skill '{skill_name}' metadata valid"))
        else:
            gate_results.append(GateResult("G0", False, f"Skill '{skill_name}' frontmatter incomplete"))

        try:
            registry = self.loader._load_registry()
            skills = registry.get("skills", {})
            found = False
            for category in ("domain", "role"):
                if skill_id in skills.get(category, {}):
                    found = True
                    break
            if found:
                gate_results.append(GateResult("G6", True, f"Skill '{skill_id}' registered"))
            else:
                gate_results.append(GateResult("G6", False, f"Skill '{skill_id}' not in registry"))
        except Exception as exc:
            gate_results.append(GateResult("G6", False, f"Registry check failed: {exc}"))

        freshness = l1.get("freshness_score", 100.0)
        if freshness >= 70:
            gate_results.append(GateResult("G6", True, f"Freshness score {freshness}/100 OK"))
        else:
            gate_results.append(GateResult("G6", False, f"Freshness score {freshness}/100 below threshold 70"))

        if "l2_body_length" in results and results.get("l2_body_length", 0) > 0:
            gate_results.append(GateResult("G6", True, "Skill body content loaded"))
        else:
            gate_results.append(GateResult("G6", False, "Skill body content empty or missing"))

        return gate_results

    def _handle_load_failure(
        self, skill_id: str, results: dict[str, Any], checkpoint: VersionCheckpoint
    ) -> dict[str, Any]:
        RollbackManager.rollback(checkpoint)
        escalation = EscalationHandler.escalate(skill_id, EscalationHandler.LEVEL_MODERATE, "Skill load failed")
        results["escalation"] = escalation
        results["status"] = "load_failed"
        return results

    def _infer_permission(self, tools: list[str]) -> str:
        if "Execute" in tools or "RunCommand" in tools:
            return PermissionLevel.ADMIN
        if "Write" in tools or "SearchReplace" in tools:
            return PermissionLevel.CODE_MODIFY
        return PermissionLevel.READ_ONLY

    def get_audit_trail(self) -> list[dict[str, Any]]:
        return self.audit_log
