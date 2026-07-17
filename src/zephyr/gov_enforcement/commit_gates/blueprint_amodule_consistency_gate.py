# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 [A_module] module_id 头部时，module_id 不得匹配 MOD-{UPPER}_{lowercase} malformation（层码后下划线+小写，如 MOD-INF_a2a_xxx）；tests/豁免；docstring 行豁免；git diff 不可达 fail-open；检出违规则 fail-closed 阻断
# [MODIFY-GUARD] gate_id="BLUEPRINT-AMODULE-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；diff-based 只检测 added 行
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_amodule_consistency_gate.py
# [A_module] module_id=MOD-GOV-blueprint_amodule_consistency_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""blueprint_amodule_consistency_gate.py — [A_module] 头部 module_id 格式一致性门禁

裁定#ARCH-DRIFT-PREVENTION-001 (ADP-3)：从"检测驱动"转向"约束驱动"。

检测 staged .py 文件 added 行中的 ``[A_module] module_id=XXX`` 头部，校验 XXX
不匹配 ``MOD-{UPPER}_{lowercase}`` malformation 模式（层码后下划线+小写）。

治本动机
--------
a2a_agent_blocklist.py 重命名时，AI 将 [A_module] 改为
``MOD-INF_a2a_agent_blocklist``——层码 INF 后用下划线+小写名，既非 track 1
（``MOD-INF-NNN`` 需 dash+序号）也非 track 2（``MOD-GOV-name`` 需 dash+名），
也非 track 2 多段域（``MOD-INFRA_A2A-NNN`` 需全大写下划线段）。此 malformation
导致 module_id_consistency_gate（跨文件碰撞检测）和 BLUEPRINT-FORMAT
（[BLUEPRINT] 格式检测）均未覆盖——ADP-3 填补此 gap。

设计权衡
--------
1. **不用 is_valid_module_id**：现有 gate 的 [A_module] 普遍使用小写名约定
   （如 ``MOD-GOV-domain_fk_gate``），而 ``validate_module_id_naming`` 的
   track 2 正则要求全大写（``[A-Z]{1,20}``），直接复用会误阻断全部现有文件。
2. **靶向 malformation 正则**：``MOD-[A-Z]+_[a-z]`` 精确匹配"层码后下划线+
   小写"的唯一错误模式，不影响 ``MOD-GOV-name``（dash 后小写）或
   ``MOD-INFRA_A2A``（下划线后大写）等合法格式。
3. **diff-based**：只检测 added 行；存量违规由 Phase 4 修复。
4. **priority=79**：在 GATE-DOMAIN-FK(78) 之后、VOCAB-HARDCODE(80) 之前。

合法 vs 非法示例
----------------
  合法: MOD-GOV-domain_fk_gate     (track 2 文件级: MOD-{DOM}-{name})
  合法: MOD-INF-025                (track 1 层码: MOD-{LAYER}-{SEQ})
  合法: MOD-INFRA_A2A-005          (track 2 多段域: MOD-{DOM}_{DOM}-{SEQ})
  合法: SH-DB-001                  (track 3 共享: SH-{ABBR}-{NNN})
  非法: MOD-INF_a2a_agent_blocklist (层码后下划线+小写 → malformation)

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate import (
        make_blueprint_amodule_consistency_gate,
    )
    registry.register(make_blueprint_amodule_consistency_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_blueprint_amodule_consistency_gate"]

# 匹配 [A_module] module_id=XXX 或 [A_module] module_id:XXX 头部
# 与 module_id_consistency_gate._RE_HEADER_MODULE_ID 一致（支持 = 和 : 分隔符）
_RE_AMODULE_HEADER = re.compile(
    r"^#\s*\[A_\w+\]\s*module_id[:=]\s*(\S+)"
)

# Malformation 正则：MOD-{UPPER}_{lowercase}
# 层码（全大写短段）后紧跟下划线+小写 = 既非 track 1（需 dash+序号）
# 也非 track 2（dash+名 或 全大写下划线段）
_MALFORMATION_RE = re.compile(r"^MOD-[A-Z]+_[a-z]")


def _check_amodule_format(
    gateway, py_files: list[str]
) -> list[str]:
    """校验 staged .py 文件 added 行的 [A_module] module_id 格式。

    diff-based 检测：只检查 added 行中的 [A_module] 声明。新文件全行 added
    故 [A_module] 必被检查；modified 文件仅当 [A_module] 行被改动时才检查。
    """
    violations: list[str] = []
    for py_file in py_files:
        file_content = _read_staged_file(gateway, py_file)
        docstring_lines = (
            _extract_docstring_lines(file_content) if file_content else set()
        )
        for line_no, content in _get_added_lines(
            gateway, py_file, "BLUEPRINT-AMODULE-CONSISTENCY"
        ):
            if line_no in docstring_lines:
                continue
            m = _RE_AMODULE_HEADER.search(content)
            if not m:
                continue
            module_id = m.group(1)
            if _MALFORMATION_RE.match(module_id):
                violations.append(
                    f"  {py_file}:{line_no}: [A_module] module_id="
                    f"'{module_id}' 格式错误——层码后下划线+小写"
                    f"（应为 MOD-{{LAYER}}-NNN 或 MOD-{{DOM}}-name）"
                )
    return violations


def _format_amodule_violations(violations: list[str]) -> tuple[bool, str]:
    """格式化 [A_module] 格式违规为阻断消息。"""
    return False, (
        "BLUEPRINT-AMODULE-CONSISTENCY：[A_module] module_id 格式不合规\n"
        "  裁定#ARCH-DRIFT-PREVENTION-001 (ADP-3)\n"
        "  合法格式（裁定#208 双轨制 + 文件级约定）：\n"
        "    track 1: MOD-{LAYER}-{SEQ}     如 MOD-INF-025\n"
        "    track 2: MOD-{DOM}-{name}      如 MOD-GOV-domain_fk_gate\n"
        "    track 2: MOD-{DOM}_{DOM}-{SEQ} 如 MOD-INFRA_A2A-005\n"
        "    track 3: SH-{ABBR}-{NNN}       如 SH-DB-001\n"
        "  非法：MOD-{UPPER}_{lowercase}    如 MOD-INF_a2a_agent_blocklist\n"
        + "\n".join(violations)
        + "\n-> 修复 [A_module] module_id，使用合法的 dash/序号 格式"
    )


def make_blueprint_amodule_consistency_gate() -> GateSpec:
    """构造 [A_module] 格式一致性门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-AMODULE-CONSISTENCY", priority=79)。
        priority=79——在 GATE-DOMAIN-FK(78) 之后、VOCAB-HARDCODE(80) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "BLUEPRINT-AMODULE-CONSISTENCY")
            if not is_test_exempt(f)
        ]
        if not py_files:
            return True, ""

        violations = _check_amodule_format(gateway, py_files)
        if violations:
            logger.error(
                "BLUEPRINT-AMODULE-CONSISTENCY gate block: %d violation(s)",
                len(violations),
            )
            return _format_amodule_violations(violations)
        return True, ""

    return GateSpec(
        gate_id="BLUEPRINT-AMODULE-CONSISTENCY",
        check=_check,
        priority=79,
    )
