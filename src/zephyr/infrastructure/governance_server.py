# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.governance_server
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.governance.drift_detection.cold_start; zephyr.governance.drift_detection.drift_engine; zephyr.governance.drift_detection.drift_models; zephyr.governance.drift_detection.drift_infrastructure; zephyr.shared.contracts.identity.agent_identity; zephyr.shared.contracts.skill_protocol; zephyr.governance.audit_trail.writer; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_governance_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""GovernanceServer: 治理域统一MCP入口
========================================
Server   : governance
Protocol :  (stdio, JSON-RPC 2.0)
Backend  : zephyr.governance.* 八件套治理模块

暴露工具
--------
- governance.check_phase_gates   — 运行指定 Phase 门禁检查
- governance.audit_registration  — 扫描孤儿文件/未注册资产
- governance.lock_status         — 查询文件锁状态
- governance.validate_contract   — 校验治理契约合规性
- governance.get_governance_health — 治理域全景健康检查
- governance.drift_scan          — 漂移检测扫描
- governance.drift_report        — 漂移检测报告与趋势分析
- governance.drift_budget        — 漂移预算检查
- governance.rbac_check          — RBAC 权限判定
- governance.list_skills         — 列出可用 Agent Skills
- governance.load_skill          — 加载指定 Agent Skill
- governance.write_audit         — 写入审计记录
- governance.execute_rollback    — 执行回滚操作
- governance.escalate            — 触发升级评估
- governance.escalation_status   — 查询升级引擎状态（熔断器/经济护栏/活跃数）
- governance.escalation_resolve  — 解决升级事件
- governance.check_budget        — 检查预算状态
"""

from __future__ import annotations

import importlib
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from zephyr.infrastructure._base_server import BaseMCPServer
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

# 5.22.10 修复：原13处 except ImportError 静默吞掉（无日志无告警无metrics），
# 用户调用 MCP 工具收到 error dict 无从知晓是依赖缺失还是逻辑错误。
# 现统一通过 logger.warning 记录依赖缺失，便于排查。
logger = logging.getLogger(__name__)

__all__ = ["GovernanceServer", "create_server"]



def _run_script(script_rel: str, *args: str) -> dict[str, Any]:
    script_path = REPO_ROOT / script_rel
    cmd = [sys.executable, str(script_path), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[-4000:] if len(result.stdout) > 4000 else result.stdout,
            "stderr": result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT (60s)", "success": False}
    except FileNotFoundError:
        return {"exit_code": -2, "stdout": "", "stderr": f"Script not found: {script_rel}", "success": False}


def _import_check(module_path: str) -> dict[str, Any]:
    import importlib

    try:
        mod = importlib.import_module(module_path)
        return {"importable": True, "has_all": bool(getattr(mod, "__all__", None)), "module": module_path}
    except ImportError as e:
        logger.exception("import failed")
        return {"importable": False, "error": "import failed", "module": module_path}
    except Exception as e:
        logger.exception("import failed", exc_info=True)
        return {"importable": False, "error": "import failed", "module": module_path}


class GovernanceServer(BaseMCPServer):
    """治理域统一 MCP Server 实现。"""

    SERVER_ID = "governance"
    VERSION = "1.1.0"
    DESCRIPTION = "治理域八件套统一MCP入口 — PhaseGate/Audit/Lock/Contract/Health/Drift/RBAC/Skill/Rollback/Escalation/Budget 十七工具"

    def __init__(self, *, enable_rbac: bool = True) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)

        self.register_tool(
            name="governance.check_phase_gates",
            description="运行指定 Phase 门禁检查（phase_0/phase_1/phase_2）",
            input_schema={
                "type": "object",
                "required": ["phase"],
                "additionalProperties": False,
                "properties": {
                    "phase": {
                        "type": "string",
                        "enum": ["phase_0", "phase_1", "phase_2"],
                        "description": "要检查的施工Phase",
                    },
                },
            },
            handler=self._check_phase_gates,
        )

        self.register_tool(
            name="governance.audit_registration",
            description="扫描项目孤儿文件/未注册资产，返回孤儿清单",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "json_output": {
                        "type": "boolean",
                        "description": "是否返回JSON格式",
                        "default": True,
                    },
                },
            },
            handler=self._audit_registration,
        )

        self.register_tool(
            name="governance.lock_status",
            description="查询文件锁状态（可指定文件或查看全部）",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "可选：要查询的具体文件路径（相对于项目根目录）",
                    },
                },
            },
            handler=self._lock_status,
        )

        self.register_tool(
            name="governance.validate_contract",
            description="校验指定的治理契约（G-CT-001~G-CT-008）合规性",
            input_schema={
                "type": "object",
                "required": ["contract_id"],
                "additionalProperties": False,
                "properties": {
                    "contract_id": {
                        "type": "string",
                        "description": "契约ID，如 G-CT-001",
                    },
                },
            },
            handler=self._validate_contract,
        )

        self.register_tool(
            name="governance.get_governance_health",
            description="治理域全景健康检查 — 锁状态/注册完整性/契约合规/模块导入 四维诊断",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._get_governance_health,
        )

        self.register_tool(
            name="governance.drift_scan",
            description="运行漂移检测扫描 — 检测模块文件与蓝图/契约之间的漂移",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "module_dir": {
                        "type": "string",
                        "description": "要扫描的模块目录路径（相对于项目根），默认扫描 behavioral-auditor 自身",
                    },
                    "level": {
                        "type": "string",
                        "enum": ["LIGHT", "STANDARD", "DEEP"],
                        "description": "扫描深度级别：LIGHT(仅HIGH) / STANDARD(HIGH+MEDIUM) / DEEP(全部)",
                        "default": "STANDARD",
                    },
                },
            },
            handler=self._drift_scan,
        )

        self.register_tool(
            name="governance.drift_report",
            description="获取漂移检测报告 — 最近扫描的健康指数和趋势分析",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._drift_report,
        )

        self.register_tool(
            name="governance.drift_budget",
            description="检查漂移预算 — 当前模块的漂移容忍度剩余量",
            input_schema={
                "type": "object",
                "required": ["module_id"],
                "additionalProperties": False,
                "properties": {
                    "module_id": {
                        "type": "string",
                        "description": "模块ID，如 MOD-INF-023",
                    },
                },
            },
            handler=self._drift_budget,
        )

        self.register_tool(
            name="governance.rbac_check",
            description="RBAC 权限判定 — 检查指定 Agent 身份是否有权执行指定操作",
            input_schema={
                "type": "object",
                "required": ["session_id", "operation"],
                "additionalProperties": False,
                "properties": {
                    "session_id": {"type": "string", "description": "Agent session ID"},
                    "operation": {
                        "type": "string",
                        "description": "操作权限，如 read:docs / write:src / execute:scripts",
                    },
                    "maturity": {
                        "type": "string",
                        "enum": ["L0_INTERN", "L1_JUNIOR", "L2_REGULAR", "L3_SENIOR", "L4_PRINCIPAL"],
                        "default": "L2_REGULAR",
                    },
                    "role": {
                        "type": "string",
                        "enum": ["reader", "writer", "executor", "admin", "auditor"],
                        "default": "executor",
                    },
                },
            },
            handler=self._rbac_check,
        )

        self.register_tool(
            name="governance.list_skills",
            description="列出所有已注册的 Agent Skills 及其触发关键词",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "keyword": {"type": "string", "description": "可选：按关键词过滤 Skill"},
                },
            },
            handler=self._list_skills,
        )

        self.register_tool(
            name="governance.load_skill",
            description="加载指定 Agent Skill 的完整上下文（渐进式披露）",
            input_schema={
                "type": "object",
                "required": ["skill_id"],
                "additionalProperties": False,
                "properties": {
                    "skill_id": {"type": "string", "description": "Skill ID，如 SKILL-DOM-GOV-001"},
                },
            },
            handler=self._load_skill,
        )

        self.register_tool(
            name="governance.write_audit",
            description="写入不可变审计记录 — 记录操作事件到审计链",
            input_schema={
                "type": "object",
                "required": ["event_type", "description"],
                "additionalProperties": False,
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "事件类型，如 file_write / gate_check / permission_deny",
                    },
                    "description": {"type": "string", "description": "事件描述"},
                    "agent_id": {"type": "string", "description": "可选：Agent session ID"},
                    "target_path": {"type": "string", "description": "可选：操作目标路径"},
                },
            },
            handler=self._write_audit,
        )

        self.register_tool(
            name="governance.execute_rollback",
            description="执行回滚操作 — 回退到指定 checkpoint 或自动回滚最近变更",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "checkpoint_id": {"type": "string", "description": "可选：回退到指定 checkpoint ID"},
                    "scope": {
                        "type": "string",
                        "enum": ["last_change", "session", "full"],
                        "default": "last_change",
                        "description": "回滚范围",
                    },
                    "dry_run": {"type": "boolean", "default": True, "description": "是否仅模拟回滚（默认安全模式）"},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "可选：仅回滚指定文件列表"},
                },
            },
            handler=self._execute_rollback,
        )

        self.register_tool(
            name="governance.escalate",
            description="触发升级评估 — 根据事件描述判定升级级别",
            input_schema={
                "type": "object",
                "required": ["category", "description"],
                "additionalProperties": False,
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "security_violation",
                            "deadlock",
                            "budget_exceeded",
                            "cascade_failure",
                            "auto_guard_failure",
                            "drift_detected",
                            "timeout",
                            "quality_degradation",
                            "owner_absent",
                            "reward_hacking_rebound",
                            "custom",
                        ],
                        "description": "事件类别",
                    },
                    "description": {"type": "string", "description": "事件描述"},
                    "owner_id": {"type": "string", "description": "可选：事件发起者 ID"},
                },
            },
            handler=self._escalate,
        )

        self.register_tool(
            name="governance.check_budget",
            description="检查预算状态 — Token/Cost/Time 三维预算消耗与剩余",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "dimension": {
                        "type": "string",
                        "enum": ["TOKEN", "COST", "TIME", "ALL"],
                        "default": "ALL",
                        "description": "预算维度",
                    },
                },
            },
            handler=self._check_budget,
        )

        self.register_tool(
            name="governance.escalation_status",
            description="查询升级引擎当前状态 — 熔断器/经济护栏/活跃升级数",
            input_schema={
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._escalation_status,
        )

        self.register_tool(
            name="governance.escalation_resolve",
            description="解决升级事件 — 标记事件为已解决并更新熔断器",
            input_schema={
                "type": "object",
                "required": ["category", "description"],
                "additionalProperties": False,
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "security_violation",
                            "deadlock",
                            "budget_exceeded",
                            "cascade_failure",
                            "auto_guard_failure",
                            "drift_detected",
                            "timeout",
                            "quality_degradation",
                            "owner_absent",
                            "reward_hacking_rebound",
                            "custom",
                        ],
                        "description": "事件类别",
                    },
                    "description": {"type": "string", "description": "事件描述"},
                    "owner_id": {"type": "string", "description": "可选：事件发起者 ID"},
                },
            },
            handler=self._escalation_resolve,
        )

    def _check_phase_gates(self, phase: str) -> dict[str, Any]:
        result = _run_script("scripts/lock_files.py", "status")
        gate_modules = {
            "phase_0": [
                "zephyr.governance.agent_rbac",
                "zephyr.governance.policy_manager",
            ],
            "phase_1": [
                "zephyr.governance.audit_trail",
                "zephyr.governance.rollback",
                "zephyr.governance.escalation",
                "zephyr.governance.drift_detection",
            ],
            "phase_2": [
                "zephyr.infrastructure.budget_enforcement",
                "zephyr.governance.a2a",
            ],
        }
        modules = gate_modules.get(phase, [])
        imports = {m: _import_check(m) for m in modules}
        all_pass = all(v.get("importable", False) for v in imports.values())
        return {
            "phase": phase,
            "modules_checked": len(modules),
            "all_importable": all_pass,
            "details": imports,
            "lock_status": result.get("stdout", ""),
        }

    def _audit_registration(self, json_output: bool = True) -> dict[str, Any]:
        args = ["--json"] if json_output else []
        result = _run_script("scripts/governance/d11_compliance/audit_registration.py", *args)
        return {
            "exit_code": result["exit_code"],
            "success": result["success"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "has_orphans": result["exit_code"] == 1,
        }

    def _lock_status(self, file_path: str | None = None) -> dict[str, Any]:
        if file_path:
            result = _run_script("scripts/lock_files.py", "check", file_path)
        else:
            result = _run_script("scripts/lock_files.py", "status")
        return {
            "query": file_path or "all",
            "exit_code": result["exit_code"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }

    def _validate_contract(self, contract_id: str) -> dict[str, Any]:
        contract_tests = {
            "G-CT-001": "tests/governance/test_gct_001_rbac_to_audit.py",
            "G-CT-002": "tests/governance/test_gct_002_audit_to_rollback.py",
            "G-CT-003": "tests/governance/test_gct_003_rollback_to_escalation.py",
            "G-CT-004": "tests/governance/test_gct_004_escalation_to_rbac.py",
            "G-CT-005": "tests/governance/test_gct_005_drift_to_rollback.py",
            "G-CT-006": "tests/governance/test_gct_006_budget_to_escalation.py",
            "G-CT-007": "tests/governance/test_gct_007_spec_to_rbac_audit.py",
            "G-CT-008": "tests/governance/test_gct_008_a2a_to_rbac_escalation.py",
        }
        test_file = contract_tests.get(contract_id)
        if test_file is None:
            return {"contract_id": contract_id, "error": f"Unknown contract: {contract_id}", "valid": False}

        test_path = REPO_ROOT / test_file
        if not test_path.exists():
            return {"contract_id": contract_id, "error": f"Test file not found: {test_file}", "valid": False}

        result = _run_script(
            "-m",
            "pytest",
            str(test_path),
            "-q",
            "--tb=short",
            "--no-header",
        )
        return {
            "contract_id": contract_id,
            "test_file": test_file,
            "exit_code": result["exit_code"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "valid": result["exit_code"] == 0,
        }

    def _get_governance_health(self) -> dict[str, Any]:
        lock_status = _run_script("scripts/lock_files.py", "status")
        audit = _run_script("scripts/governance/d11_compliance/audit_registration.py")

        eight_modules = [
            "zephyr.governance.agent_rbac",
            "zephyr.governance.policy_manager",
            "zephyr.governance.audit_trail",
            "zephyr.governance.rollback",
            "zephyr.governance.escalation",
            "zephyr.governance.drift_detection",
            "zephyr.infrastructure.budget_enforcement",
            "zephyr.governance.a2a",
        ]
        imports = {m: _import_check(m) for m in eight_modules}
        importable = sum(1 for v in imports.values() if v.get("importable"))

        engine_modules = [
            "zephyr.escalation",
            "zephyr.infrastructure.budget_enforcement",
            "zephyr.a2a",
        ]
        engine_imports = {m: _import_check(m) for m in engine_modules}

        has_orphans = audit["exit_code"] == 1
        locks_active = "LOCKED" in lock_status.get("stdout", "")

        return {
            "health": "DEGRADED" if (has_orphans or importable < 8 or locks_active) else "HEALTHY",
            "modules_importable": f"{importable}/{len(eight_modules)}",
            "governance_bridge_imports": imports,
            "engine_imports": engine_imports,
            "has_orphans": has_orphans,
            "locks_active": locks_active,
            "lock_status": lock_status.get("stdout", ""),
            "audit_stderr": audit.get("stderr", "")[:500],
        }

    def _drift_scan(self, module_dir: str | None = None, level: str = "STANDARD") -> dict[str, Any]:
        try:
            from zephyr.governance.drift_detection.cold_start import init_database, init_directories
            from zephyr.governance.drift_detection.drift_engine import ScanLevel, scan

            project_root = str(REPO_ROOT)
            init_directories(project_root)
            init_database(project_root)
            scan_level = {"LIGHT": ScanLevel.LIGHT, "STANDARD": ScanLevel.STANDARD, "DEEP": ScanLevel.DEEP}.get(
                level, ScanLevel.STANDARD
            )
            target_dir = (
                str(REPO_ROOT / module_dir)
                if module_dir
                else str(REPO_ROOT / "src" / "zephyr" / "behavioral-auditor")
            )
            result = run_sync(scan(level=scan_level, scope=[target_dir] if module_dir else None))
            return {
                "scan_id": str(result.scan_id),
                "detectors_run": result.detectors_run,
                "total_drift_events": result.total_drift_events,
                "storm_mode_triggered": result.storm_mode_triggered,
                "events": [
                    {
                        "detector_id": e.detector_id,
                        "drift_dimension": e.drift_dimension,
                        "state": e.state.value,
                        "resolution_detail": e.resolution_detail,
                        "auto_fixed": e.auto_fixed,
                    }
                    for e in result.events[:50]
                ],
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("behavioral-auditor import failed failed")

            return {"error": "behavioral-auditor import failed failed", "events": []}
        except Exception as e:
            logger.exception("scan failed failed", exc_info=True)

            return {"error": "scan failed failed", "events": []}

    def _drift_report(self) -> dict[str, Any]:
        try:
            from zephyr.governance.drift_detection.drift_engine import build_report, load_detector_registry
            from zephyr.governance.drift_detection.drift_models import DriftReport

            detectors = load_detector_registry()
            active_count = sum(1 for d in detectors if d.status == "active")
            categories: dict[str, int] = {}
            for d in detectors:
                cat = getattr(d, "category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
            return {
                "total_detectors": len(detectors),
                "active_detectors": active_count,
                "categories": categories,
                "drift_dimensions_covered": len({d.drift_dimension for d in detectors if d.drift_dimension}),
                "auto_fixable_count": sum(1 for d in detectors if d.auto_fixable),
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("import failed failed")

            return {"error": "import failed failed"}
        except Exception as e:
            logger.exception("report failed failed", exc_info=True)

            return {"error": "report failed failed"}

    def _drift_budget(self, module_id: str) -> dict[str, Any]:
        try:
            from zephyr.governance.drift_detection.drift_infrastructure import check_budget_for_gate

            result = check_budget_for_gate(module_id)
            return {
                "module_id": module_id,
                **result,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("import failed failed")

            return {"error": "import failed failed", "module_id": module_id, "allowed": False}
        except Exception as e:
            logger.exception("budget check failed failed", exc_info=True)

            return {"error": "budget check failed failed", "module_id": module_id, "allowed": False}

    def _rbac_check(
        self, session_id: str, operation: str, maturity: str = "L2_REGULAR", role: str = "executor"
    ) -> dict[str, Any]:
        try:
            from zephyr.shared.contracts.identity.agent_identity import (
                AgentIdentity,
                AgentRole,
                IDESource,
                MaturityLevel,
            )

            _perm_guard_mod = importlib.import_module("zephyr.security.access_control.guards.permission_guard")
            PermissionGuard = _perm_guard_mod.PermissionGuard

            ml = MaturityLevel(maturity)
            ar = AgentRole(role)
            identity = AgentIdentity(
                session_id=session_id, maturity=ml, role=ar, ide_source=IDESource.TRAE, owner_approved=True
            )
            guard = PermissionGuard()
            result = guard.check(identity, operation)
            return {
                "session_id": session_id,
                "operation": operation,
                "decision": result.decision.value,
                "reason": result.reason,
                "timing_ns": result.timing_ns,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("RBAC import failed failed")

            return {"error": "RBAC import failed failed", "decision": "ERROR"}
        except Exception as e:
            logger.exception("RBAC check failed failed", exc_info=True)

            return {"error": "RBAC check failed failed", "decision": "ERROR"}

    def _list_skills(self, keyword: str | None = None) -> dict[str, Any]:
        try:
            from zephyr.shared.contracts.skill_protocol import create_skill_loader

            loader = create_skill_loader()
            skills = loader.list_skills()
            if keyword:
                skills = [s for s in skills if keyword.lower() in str(s).lower()]
            return {
                "total_skills": len(skills),
                "keyword_filter": keyword,
                "skills": [
                    {
                        "id": getattr(s, "skill_id", str(s)),
                        "name": getattr(s, "name", str(s)),
                        "triggers": getattr(s, "trigger_keywords", []),
                    }
                    for s in skills[:50]
                ],
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Agent Spec import failed failed")

            return {"error": "Agent Spec import failed failed", "total_skills": 0, "skills": []}
        except Exception as e:
            logger.exception("list_skills failed failed", exc_info=True)

            return {"error": "list_skills failed failed", "total_skills": 0, "skills": []}

    def _load_skill(self, skill_id: str) -> dict[str, Any]:
        try:
            from zephyr.shared.contracts.skill_protocol import create_skill_loader

            loader = create_skill_loader()
            skill = loader.load(skill_id)
            if skill is None:
                return {"skill_id": skill_id, "loaded": False, "error": "Skill not found"}
            return {
                "skill_id": skill_id,
                "loaded": True,
                "name": getattr(skill, "name", ""),
                "description": getattr(skill, "description", ""),
                "context_size": len(str(getattr(skill, "context", ""))),
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Agent Spec import failed")

            return {"skill_id": skill_id, "loaded": False, "error": "Agent Spec import failed"}
        except Exception as e:
            logger.exception("load failed", exc_info=True)

            return {"skill_id": skill_id, "loaded": False, "error": "load failed"}

    def _write_audit(
        self, event_type: str, description: str, agent_id: str | None = None, target_path: str | None = None
    ) -> dict[str, Any]:
        try:
            from zephyr.governance.audit_trail.writer import AuditWriter

            writer = AuditWriter()
            entry_id = writer.write(
                event_type=event_type,
                description=description,
                agent_id=agent_id or "mcp-governance",
                target_path=target_path,
            )
            return {"entry_id": entry_id, "written": True, "event_type": event_type}
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Audit Trail import failed")

            return {"written": False, "error": "Audit Trail import failed"}
        except Exception as e:
            logger.exception("write_audit failed", exc_info=True)

            return {"written": False, "error": "write_audit failed"}

    def _execute_rollback(
        self,
        checkpoint_id: str | None = None,
        scope: str = "last_change",
        dry_run: bool = True,
        files: list[str] | None = None,
    ) -> dict[str, Any]:
        try:
            from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor

            executor = RollbackExecutor()

            if dry_run:
                pf = executor.preflight_check()
                preview_data: dict[str, Any] = {}
                if checkpoint_id:
                    preview = executor.preview(checkpoint_id)
                    preview_data = {
                        "changed_files": preview.changed_files,
                        "conflict_risk": preview.conflict_risk,
                        "estimated_change_bytes": preview.estimated_change_bytes,
                    }
                return {
                    "dry_run": True,
                    "preflight_passed": pf.passed,
                    "preflight_errors": pf.errors if hasattr(pf, "errors") else [],
                    "scope": scope,
                    "checkpoint_id": checkpoint_id,
                    "preview": preview_data,
                }

            if files:
                if not checkpoint_id:
                    import subprocess as _sp

                    head = _sp.run(
                        ["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=str(executor._project_root),
                    )
                    checkpoint_id = head.stdout.strip() if head.returncode == 0 else ""

                rollback_result = executor.rollback_or_discard(
                    files, commit_sha=checkpoint_id, audit_session="mcp-governance"
                )
                return {
                    "dry_run": False,
                    "success": rollback_result.success,
                    "decision": rollback_result.decision.value,
                    "files_discarded": rollback_result.files_discarded,
                    "files_blocked": rollback_result.files_blocked,
                    "scope": scope,
                    "checkpoint_id": checkpoint_id,
                }

            if not checkpoint_id:
                import subprocess as _sp

                head = _sp.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(executor._project_root),
                )
                checkpoint_id = head.stdout.strip() if head.returncode == 0 else ""
                if not checkpoint_id:
                    return {"error": "Cannot determine HEAD commit SHA", "success": False}

            rollback_result = executor.full_revert(checkpoint_id, audit_session="mcp-governance")
            return {
                "dry_run": False,
                "success": rollback_result.success,
                "operation": rollback_result.operation.value,
                "commit_sha": rollback_result.commit_sha,
                "files_reverted": rollback_result.files_reverted,
                "db_tables_restored": rollback_result.db_tables_restored,
                "db_rows_restored": rollback_result.db_rows_restored,
                "execution_id": rollback_result.execution_id,
                "errors": rollback_result.errors,
                "scope": scope,
                "checkpoint_id": checkpoint_id,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Rollback import failed failed")

            return {"error": "Rollback import failed failed", "success": False}
        except Exception as e:
            logger.exception("rollback failed failed", exc_info=True)

            return {"error": "rollback failed failed", "success": False}

    def _escalate(self, category: str, description: str, owner_id: str | None = None) -> dict[str, Any]:
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine
            from zephyr.governance.escalation.escalation_models import RuleCategory

            engine = EscalationEngine("mcp-governance")
            cat = RuleCategory(category)
            event = engine.evaluate(cat, description, owner_id=owner_id)
            return {
                "category": category,
                "level": event.level.value,
                "state": event.state.value,
                "event_id": event.event_id,
                "description": description,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Escalation import failed failed")

            return {"error": "Escalation import failed failed", "level": "UNKNOWN"}
        except Exception as e:
            logger.exception("escalate failed failed", exc_info=True)

            return {"error": "escalate failed failed", "level": "UNKNOWN"}

    def _check_budget(self, dimension: str = "ALL") -> dict[str, Any]:
        try:
            from zephyr.governance.ops_governance.budget_engine import BudgetEngine
            from zephyr.governance.ops_governance.budget_models import BudgetDimension

            engine = BudgetEngine()
            dims = (
                [BudgetDimension.TOKEN, BudgetDimension.COST, BudgetDimension.TIME]
                if dimension == "ALL"
                else [BudgetDimension(dimension)]
            )
            result = {}
            for dim in dims:
                policy = engine.get_active_policy(dim)
                if policy:
                    result[dim.name] = {
                        "daily_limit": policy.daily_limit,
                        "hourly_limit": policy.hourly_limit,
                        "per_request_limit": policy.per_request_limit,
                    }
            consumption = engine.get_consumption_summary()
            return {
                "policies": result,
                "consumption": consumption,
                "degradation_level": engine.current_degradation_level.value,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Budget Enforcer import failed failed")

            return {"error": "Budget Enforcer import failed failed"}
        except Exception as e:
            logger.exception("check_budget failed failed", exc_info=True)

            return {"error": "check_budget failed failed"}

    def _escalation_status(self) -> dict[str, Any]:
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine

            engine = EscalationEngine("mcp-status")
            return {
                "circuit_state": engine.get_circuit_state().name,
                "economic_status": engine.get_economic_status(),
                "active_count": engine.get_active_count(),
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Escalation import failed failed")

            return {"error": "Escalation import failed failed"}
        except Exception as e:
            logger.exception("escalation_status failed failed", exc_info=True)

            return {"error": "escalation_status failed failed"}

    def _escalation_resolve(self, category: str, description: str, owner_id: str | None = None) -> dict[str, Any]:
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine
            from zephyr.governance.escalation.escalation_models import RuleCategory

            engine = EscalationEngine("mcp-resolve")
            cat = RuleCategory(category)
            event = engine.evaluate(cat, description, owner_id=owner_id)
            engine.record_resolution(event)
            return {
                "category": category,
                "level": event.level.value,
                "state": event.state.value,
                "event_id": event.event_id,
                "resolved": True,
            }
        except ImportError as e:
            logger.warning("ImportError in handler: %s", e, exc_info=True)
            logger.exception("Escalation import failed failed")

            return {"error": "Escalation import failed failed", "resolved": False}
        except Exception as e:
            logger.exception("escalation_resolve failed failed", exc_info=True)

            return {"error": "escalation_resolve failed failed", "resolved": False}


def create_server() -> GovernanceServer:
    return GovernanceServer()


if __name__ == "__main__":
    import json as _json

    server = GovernanceServer()
    health = server._get_governance_health()
    print(_json.dumps(health, indent=2, ensure_ascii=False))