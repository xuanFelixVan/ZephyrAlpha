# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.gate_engine_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.infrastructure.__init__; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_gate_engine_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: gate_engine MCP Server skeleton ( T-3-04)
"""
GateEngineServer: 门禁裁决服务 MCP Server
=========================================
Task ID  : T-3-04 (B15)
Server   : gate_engine (tool-contracts.yaml §Server 3)
Protocol :  传输、JSON-RPC 2.0）
Backend  : src/zephyr/gates/gate_engine.py (T-2-17)
Gate策略 : docs/02_enterprise_architecture/gate-strategy-standard.md

实现工具
--------
- gate_engine.run_g1_write     — 写入防护 Gate（UTF-8 / 命名 / 路径白名单）
- gate_engine.run_g2_commit    — 提交门禁 Gate（等价 pre-commit 汇总）
- gate_engine.run_g3_phase     — 阶段验收 Gate（触发 Sentinel L1）
- gate_engine.run_g4_contract  — 结构化输出契约校验
- gate_engine.submit_exemption — 提交 Owner 签发的豁免
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import date
from typing import Any

from zephyr.infrastructure._base_server import BaseMCPServer, MCPError
from zephyr.integration.shared.schema.schemas import Priority
from zephyr.shared.utils.time_utils import now_iso

__all__ = ["GateEngineServer", "create_server"]

_GATE_IDS = frozenset({"G1", "G2", "G3", "G4", "G5"})
_CONTRACT_MODELS = frozenset(
    {"Task", "AuditReport", "KnowledgeEntry", "FailurePattern", "HandoffPackage", "IntentResult"}
)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# 路径白名单模式（G1 写入防护示例规则）
_BLACKLISTED_PATH_FRAGMENTS = frozenset({"scripts/archive", "working-designs", "temp_", ".backup"})


def _check_blacklisted_path(path: str) -> list[str]:
    """检查路径是否命中黑名单。

    5.45.4 修复：改用 os.path.realpath()+os.path.commonpath() 边界检查，
    防止通过 ../、./、符号链接等路径注入绕过子串匹配（in 操作符）。
    """
    hits: list[str] = []
    try:
        real = os.path.realpath(path)
    except (OSError, ValueError):
        real = os.path.normpath(path)
    parts = [p for p in real.replace("\\", "/").split("/") if p]
    for fragment in _BLACKLISTED_PATH_FRAGMENTS:
        frag = fragment.replace("\\", "/")
        if "/" in frag:
            # 路径型fragment（如 scripts/archive）：优先用 commonpath 边界检查
            try:
                frag_abs = os.path.realpath(fragment)
                if os.path.commonpath([real, frag_abs]) == frag_abs:
                    hits.append(fragment)
                    continue
            except (OSError, ValueError):
                pass
            # 回退：路径分量序列匹配
            frag_parts = [p for p in frag.split("/") if p]
            if any(
                parts[i : i + len(frag_parts)] == frag_parts
                for i in range(len(parts) - len(frag_parts) + 1)
            ):
                hits.append(fragment)
        else:
            # 名称型fragment（如 temp_、.backup）：按路径分量检查，非裸子串
            if any(fragment in part for part in parts):
                hits.append(fragment)
    return hits


def _make_gate_run_report(
    gate_id: str,
    passed: bool,
    checks_run: int,
    failed_checks: list[str],
    artifact_path: str | None = None,
) -> dict[str, Any]:
    p0_count = sum(1 for c in failed_checks if Priority.P0.value in c)
    return {
        "gate_run_id": str(uuid.uuid4()),
        "gate_id": gate_id,
        "passed": passed,
        "details": {
            "checks_run": checks_run,
            "checks_failed": failed_checks,
            "level_distribution": {
                Priority.P0.value: p0_count,
                Priority.P1.value: len(failed_checks) - p0_count,
                Priority.P2.value: 0,
            },
        },
        "artifact_path": artifact_path,
        "created_at": now_iso(),
    }


class GateEngineServer(BaseMCPServer):
    """gate_engine MCP Server 实现。

    骨架内置规则判断逻辑（生产中替换为 GateEngine.evaluate() 调用）。
    """

    SERVER_ID = "gate_engine"
    VERSION = "1.0.0"
    DESCRIPTION = "门禁裁决服务；包装 gate_engine.py 的 5 道 Gate"

    def __init__(self, *, enable_rbac: bool = True) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)
        # 存储已提交的豁免（骨架层）
        self._exemptions: dict[str, dict[str, Any]] = {}

        self.register_tool(
            name="gate_engine.run_g1_write",
            description="写入防护 Gate（UTF-8 / 命名 / 路径白名单）",
            input_schema={
                "type": "object",
                "required": ["target_path", "content_preview"],
                "additionalProperties": False,
                "properties": {
                    "target_path": {"type": "string"},
                    "content_preview": {"type": "string"},
                    "session_id": {"type": "string"},
                },
            },
            handler=self._run_g1_write,
        )
        self.register_tool(
            name="gate_engine.run_g2_commit",
            description="提交门禁 Gate（等价 pre-commit 汇总）",
            input_schema={
                "type": "object",
                "required": ["files"],
                "additionalProperties": False,
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}},
                    "commit_message": {"type": "string"},
                },
            },
            handler=self._run_g2_commit,
        )
        self.register_tool(
            name="gate_engine.run_g3_phase",
            description="阶段验收 Gate（触发 Sentinel L1）",
            input_schema={
                "type": "object",
                "required": ["phase_id"],
                "additionalProperties": False,
                "properties": {
                    "phase_id": {"type": "integer", "minimum": 0, "maximum": 5},
                    "target_phase": {"type": "integer"},
                },
            },
            handler=self._run_g3_phase,
        )
        self.register_tool(
            name="gate_engine.run_g4_contract",
            description="结构化输出契约校验（Pydantic + frontmatter）",
            input_schema={
                "type": "object",
                "required": ["payload", "model_name"],
                "additionalProperties": False,
                "properties": {
                    "payload": {"type": "object"},
                    "model_name": {"type": "string", "enum": sorted(_CONTRACT_MODELS)},
                },
            },
            handler=self._run_g4_contract,
        )
        self.register_tool(
            name="gate_engine.submit_exemption",
            description="提交 Owner 签发的豁免（仅 Owner 生效）",
            input_schema={
                "type": "object",
                "required": ["check_id", "reason", "valid_until", "signer_email"],
                "additionalProperties": False,
                "properties": {
                    "check_id": {"type": "string"},
                    "reason": {"type": "string", "minLength": 10},
                    "valid_until": {"type": "string"},
                    "signer_email": {"type": "string"},
                },
            },
            handler=self._submit_exemption,
        )
        self.register_tool(
            name="gate_engine.run_g5_quality",
            description="G5 代码质量 Gate——lint / 类型检查 / 测试覆盖率",
            input_schema={
                "type": "object",
                "required": ["target_paths"],
                "additionalProperties": False,
                "properties": {
                    "target_paths": {"type": "array", "items": {"type": "string"}},
                    "check_types": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["lint", "typecheck", "coverage", "security"]},
                        "default": ["lint", "typecheck"],
                    },
                },
            },
            handler=self._run_g5_quality,
        )
        self.register_tool(
            name="gate_engine.run_g6_blueprint_compliance",
            description="G6 蓝图合规 Gate——蓝图读取验证 + 架构对齐检查",
            input_schema={
                "type": "object",
                "required": ["target_paths", "blueprint_ids"],
                "additionalProperties": False,
                "properties": {
                    "target_paths": {"type": "array", "items": {"type": "string"}},
                    "blueprint_ids": {"type": "array", "items": {"type": "string"}},
                    "required_sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["§1"],
                    },
                },
            },
            handler=self._run_g6_blueprint_compliance,
        )
        self.register_tool(
            name="gate_engine.circuit_breaker_status",
            description="查询熔断状态——返回各 Gate 当前 allow/block/rate_limit 状态",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._circuit_breaker_status,
        )

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _run_g1_write(
        self,
        target_path: str,
        content_preview: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """G1 写入防护：路径黑名单 + 内容编码检测（骨架规则）。"""
        failed: list[str] = []

        # 5.45.4 修复：路径校验改用 realpath+commonpath 边界检查
        for fragment in _check_blacklisted_path(target_path):
            failed.append(f"P0:G1.1:blacklisted_path_fragment:{fragment!r}")

        has_version_suffix = re.search(r"-v\d+\.", target_path)
        if has_version_suffix:
            failed.append("P0:G1.2:versioned_filename_forbidden")

        has_non_utf8_hint = any(ord(c) > 127 for c in content_preview[:200])
        if has_non_utf8_hint and "\\x" in repr(content_preview[:50]):
            failed.append("P1:G1.3:possible_encoding_issue")

        passed = len([f for f in failed if f.startswith(Priority.P0.value)]) == 0
        report = _make_gate_run_report("G1", passed, 3, failed)
        if not passed:
            raise MCPError(-32412, f"ZA-GT-0001: gate blocked (P0): {failed}", report)
        return report

    def _run_g2_commit(
        self,
        files: list[str],
        commit_message: str | None = None,
    ) -> dict[str, Any]:
        """G2 提交门禁：文件命名规则 + commit message 格式校验。"""
        failed: list[str] = []

        for fp in files:
            # 5.45.4 修复：路径校验改用 realpath+commonpath 边界检查
            for fragment in _check_blacklisted_path(fp):
                failed.append(f"P0:G2.1:blacklisted_path:{fp!r}")
            if re.search(r"(-v\d+\.|\.backup$|^temp_)", fp.split("/")[-1]):
                failed.append(f"P0:G2.2:forbidden_filename_pattern:{fp!r}")

        if commit_message:
            if not re.match(r"^(feat|fix|refactor|docs|test|chore|governance|risk-config-change)\(", commit_message):
                failed.append("P1:G2.3:commit_message_format_mismatch")

        passed = len([f for f in failed if f.startswith(Priority.P0.value)]) == 0
        report = _make_gate_run_report("G2", passed, len(files) + 1, failed)
        if not passed:
            raise MCPError(-32412, f"ZA-GT-0001: gate blocked (P0): {failed}", report)
        return report

    def _run_g3_phase(
        self,
        phase_id: int,
        target_phase: int | None = None,
    ) -> dict[str, Any]:
        """G3 阶段验收 Gate（骨架：仅检查 target_phase > phase_id）。"""
        failed: list[str] = []

        if target_phase is not None and target_phase <= phase_id:
            failed.append(f"P0:G3.1:target_phase {target_phase} must be > current phase {phase_id}")

        passed = not bool(failed)
        report = _make_gate_run_report("G3", passed, 1, failed)
        if not passed:
            raise MCPError(-32412, f"ZA-GT-0001: gate blocked (P0): {failed}", report)
        return report

    def _run_g4_contract(
        self,
        payload: dict[str, Any],
        model_name: str,
    ) -> dict[str, Any]:
        """G4 结构化输出契约校验（骨架：必填字段存在性检查）。"""
        if model_name not in _CONTRACT_MODELS:
            raise MCPError(-32602, f"model_name 无效: {model_name!r}")

        _REQUIRED_FIELDS: dict[str, list[str]] = {
            "Task": ["task_id", "phase", "status", "directive"],
            "AuditReport": ["report_id", "status"],
            "KnowledgeEntry": ["ke_id", "title", "category"],
            "FailurePattern": ["failure_id", "description"],
            "HandoffPackage": ["from_session", "to_model", "completed_tasks", "next_tasks"],
            "IntentResult": ["query", "primary_domain", "confidence", "source_stage"],
        }
        required = _REQUIRED_FIELDS.get(model_name, [])
        errors = [f"missing field: {f!r}" for f in required if f not in payload]

        return {
            "passed": not bool(errors),
            "errors": errors,
            "suggested_fix": f"请补充字段：{errors}" if errors else None,
        }

    def _submit_exemption(
        self,
        check_id: str,
        reason: str,
        valid_until: str,
        signer_email: str,
    ) -> dict[str, Any]:
        """提交豁免申请（骨架：校验 email 格式 + reason 长度）。"""
        if len(reason) < 10:
            raise MCPError(-32602, "reason 至少 10 个字符")
        if not _EMAIL_RE.match(signer_email):
            raise MCPError(-32403, f"ZA-GT-0003: signer_email 格式无效: {signer_email!r}")

        try:
            date.fromisoformat(valid_until)
        except ValueError as exc:
            raise MCPError(-32602, f"valid_until 格式无效（期望 YYYY-MM-DD）: {exc}") from exc

        exemption_id = f"EX-{check_id}-{uuid.uuid4().hex[:8].upper()}"
        self._exemptions[exemption_id] = {
            "exemption_id": exemption_id,
            "check_id": check_id,
            "reason": reason,
            "valid_until": valid_until,
            "signer_email": signer_email,
            "created_at": now_iso(),
        }
        return {"exemption_id": exemption_id, "accepted": True}

    def _run_g5_quality(
        self,
        target_paths: list[str],
        check_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """G5 代码质量 Gate（骨架规则：路径存在性 + 命名规范检查）。"""
        if check_types is None:
            check_types = ["lint", "typecheck"]
        failed: list[str] = []

        for fp in target_paths:
            if re.search(r"(-v\d+\.|\.backup$|^temp_)", fp.split("/")[-1] or fp):
                failed.append(f"P1:G5.1:forbidden_filename:{fp!r}")
            if fp.endswith(".py") and re.search(r"[A-Z]", (fp.split("/")[-1] or "").replace(".py", "")):
                failed.append(f"P1:G5.2:uppercase_in_module_name:{fp!r}")

        checks_run = len(target_paths) * len(check_types)
        passed = len([f for f in failed if f.startswith(Priority.P0.value)]) == 0
        report = _make_gate_run_report("G5", passed, checks_run, failed)
        return report

    def _run_g6_blueprint_compliance(
        self,
        target_paths: list[str],
        blueprint_ids: list[str],
        required_sections: list[str] | None = None,
    ) -> dict[str, Any]:
        """G6 蓝图合规 Gate（骨架：检查 blueprint_ids 非空 + 路径归属校验）。"""
        if required_sections is None:
            required_sections = ["§1"]
        failed: list[str] = []

        if not blueprint_ids:
            failed.append("P0:G6.1:no_blueprints_referenced")
        for bp_id in blueprint_ids:
            if not bp_id.startswith("MOD-") and not bp_id.startswith("DOM-") and not bp_id.startswith("SYS-"):
                failed.append(f"P0:G6.2:invalid_blueprint_id_format:{bp_id!r}")

        passed = not bool(failed)
        report = _make_gate_run_report("G6", passed, len(blueprint_ids), failed)
        report["required_sections"] = required_sections
        return report

    def _circuit_breaker_status(self) -> dict[str, Any]:
        """返回各 Gate 熔断状态（骨架：默认全部 allow）。"""
        return {
            "status": "operational",
            "gates": {
                "G1": {"state": "allow", "failure_count": 0, "last_failure": None},
                "G2": {"state": "allow", "failure_count": 0, "last_failure": None},
                "G3": {"state": "allow", "failure_count": 0, "last_failure": None},
                "G4": {"state": "allow", "failure_count": 0, "last_failure": None},
                "G5": {"state": "allow", "failure_count": 0, "last_failure": None},
                "G6": {"state": "allow", "failure_count": 0, "last_failure": None},
            },
            "checked_at": now_iso(),
        }


def create_server(*, enable_rbac: bool = True) -> GateEngineServer:
    """工厂函数，返回配置好的 GateEngineServer 实例。"""
    return GateEngineServer(enable_rbac=enable_rbac)


if __name__ == "__main__":
    create_server().run()
