# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_amodule_cross_check_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件 added 行含 [BLUEPRINT] 和 [A_module] 两头部时，
# 若两值原始字符串不同但 normalize 后相等（DASH/UNDERSCORE 差异）则阻断（同模块双拼写违规）；
# 两值完全相同（同模块同拼写，项目 2284 文件惯例）放行；
# tests/豁免；docstring 行豁免；git diff 不可达 fail-open；检出违规则 fail-closed 阻断
# [MODIFY-GUARD] gate_id="BLUEPRINT-AMODULE-CROSS-CHECK"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；diff-based 只检测 added 行
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_amodule_cross_check_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""blueprint_amodule_cross_check_gate.py — [BLUEPRINT] vs [A_module] 交叉校验门禁

裁定 #ARCH-MODULE-ID-DUAL-SPELLING-001：填补 [BLUEPRINT] vs [A_module] 头部
module_id 一致性校验盲区。

现有 gate 分工：
- blueprint_format_gate（prio=77）：只校验 [BLUEPRINT] 头部格式
- blueprint_amodule_consistency_gate（prio=79）：只校验 [A_module] 头部格式
- module_id_consistency_gate（prio=88）：跨文件 [A_*] 唯一性，显式排除 [BLUEPRINT]

**盲区**：无 gate 校验同文件 [BLUEPRINT] 与 [A_module] 的 module_id 一致性。
当两头部指向同一概念模块但拼写不同（如 [BLUEPRINT]=MOD-GOV_error_pattern_library
vs [A_module]=MOD-GOV-error_pattern_library），造成同模块双拼写，违背真源唯一性。

检测逻辑
--------
1. 提取 staged .py 文件前 20 行的 [BLUEPRINT] module_id（第 1 段）
2. 提取 [A_module] module_id（module_id=VALUE）
3. 若两值原始字符串不同但 normalize 后相等（`_` 和 `-` 统一为 `-`），则阻断
   （同模块双拼写：如 MOD-GOV_foo vs MOD-GOV-foo）
4. 若两值完全相同（同模块同拼写，项目 2284 文件惯例），放行
5. 若两值指向不同模块（如 bp=MOD-GATE_ENGINE, am=MOD-GOV-xxx），放行（设计意图）

normalize 逻辑
--------------
``MOD-GOV_error_pattern_library`` → ``MOD-GOV-error_pattern_library``
``MOD-GOV-error_pattern_library``  → ``MOD-GOV-error_pattern_library``
两者 normalize 后相等 → 阻断（同模块双拼写）

``MOD-GATE_ENGINE`` → ``MOD-GATE-ENGINE``
``MOD-GOV-domain_fk_gate`` → ``MOD-GOV-domain-fk-gate``
两者不等 → 放行（不同模块）

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_amodule_cross_check_gate import (
        make_blueprint_amodule_cross_check_gate,
    )
    registry.register(make_blueprint_amodule_cross_check_gate())
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

__all__ = ["make_blueprint_amodule_cross_check_gate"]

# BP 头部正则（匹配 [BLUEPRINT] module_id | path | section 格式）
_RE_BLUEPRINT_HEADER = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)")

# [A_module] 头部正则：# [A_module] module_id=VALUE | ...
_RE_AMODULE_HEADER = re.compile(r"^#\s*\[A_\w+\]\s*module_id[:=]\s*(\S+)")

# noqa 行级逃生标记
_NOQA_MARKER = "noqa: blueprint-amodule-cross-check"


def _normalize_module_id(mid: str) -> str:
    """normalize module_id：将 ``_`` 替换为 ``-`` 用于比较。

    ``MOD-GOV_error_pattern_library`` → ``MOD-GOV-error_pattern_library``
    ``MOD-GOV-error_pattern_library``  → ``MOD-GOV-error_pattern_library``
    """
    return mid.replace("_", "-")


def _extract_headers(content: str) -> tuple[str | None, str | None]:
    """从文件内容前 20 行提取 [BLUEPRINT] 和 [A_module] 的 module_id。

    Args:
        content: 文件完整内容字符串。

    Returns:
        (blueprint_id, amodule_id)——任一不存在则为 None。
    """
    blueprint_id: str | None = None
    amodule_id: str | None = None
    for line in content.splitlines()[:20]:
        if blueprint_id is None:
            m = _RE_BLUEPRINT_HEADER.search(line)
            if m:
                blueprint_id = m.group(1)
        if amodule_id is None:
            m = _RE_AMODULE_HEADER.search(line)
            if m:
                amodule_id = m.group(1)
        if blueprint_id and amodule_id:
            break
    return blueprint_id, amodule_id


def _check_cross_consistency(
    gateway, py_files: list[str]
) -> list[str]:
    """校验 staged .py 文件的 [BLUEPRINT] vs [A_module] module_id 一致性。

    diff-based 检测：只检查有 added 行的文件。对每个待检文件读取完整内容，
    提取两头部 module_id，若 normalize 后相等则记录违规。
    """
    violations: list[str] = []
    for py_file in py_files:
        file_content = _read_staged_file(gateway, py_file)
        if not file_content:
            continue

        docstring_lines = _extract_docstring_lines(file_content)

        # 检查是否有 added 行含 noqa 逃生标记
        added_lines = list(_get_added_lines(gateway, py_file, "BLUEPRINT-AMODULE-CROSS-CHECK"))
        if not added_lines:
            continue

        has_noqa = any(_NOQA_MARKER in content for _, content in added_lines)
        if has_noqa:
            continue

        # 检查 [BLUEPRINT] 或 [A_module] 行是否在 added 行中
        # （只有头部被改动时才触发检测，避免对未改动文件误报）
        bp_in_added = any(
            _RE_BLUEPRINT_HEADER.search(content) for _, content in added_lines
            if _line_no_not_in_docstring(_, docstring_lines)
        )
        am_in_added = any(
            _RE_AMODULE_HEADER.search(content) for _, content in added_lines
            if _line_no_not_in_docstring(_, docstring_lines)
        )
        if not (bp_in_added or am_in_added):
            continue

        blueprint_id, amodule_id = _extract_headers(file_content)
        if not blueprint_id or not amodule_id:
            continue

        # 同模块双拼写判定：原始字符串不同但 normalize 后相等（DASH/UNDERSCORE 差异）
        # 2026-08-19 治本（#ARCH-130 P0-A 连带）：原逻辑仅判 normalize 相等，
        # 把"同模块同拼写"（bp==am 完全相同，项目 2284 文件惯例）误判为违规。
        # 真正的双拼写=原始不同但 normalize 后相等（如 MOD-GOV_foo vs MOD-GOV-foo）。
        if blueprint_id != amodule_id and _normalize_module_id(blueprint_id) == _normalize_module_id(amodule_id):
            violations.append(
                f"  {py_file}: [BLUEPRINT] module_id='{blueprint_id}' 与 "
                f"[A_module] module_id='{amodule_id}' 是同模块双拼写"
                f"（normalize 后均为 '{_normalize_module_id(blueprint_id)}'）"
            )
    return violations


def _line_no_not_in_docstring(line_no: int, docstring_lines: set[int]) -> bool:
    """检查行号是否不在 docstring 中。"""
    return line_no not in docstring_lines


def _format_violations(violations: list[str]) -> tuple[bool, str]:
    """格式化违规为阻断消息。"""
    return False, (
        "BLUEPRINT-AMODULE-CROSS-CHECK：[BLUEPRINT] 与 [A_module] 同模块双拼写违规\n"
        "  裁定 #ARCH-MODULE-ID-DUAL-SPELLING-001\n"
        "  规则：同一文件 [BLUEPRINT] 和 [A_module] 头部若指向同一概念模块\n"
        "  （normalize 后 module_id 相等），MUST 使用相同拼写\n"
        "  normalize 逻辑：将 _ 替换为 - 后比较\n"
        "  合法：[BLUEPRINT]=MOD-GATE_ENGINE, [A_module]=MOD-GOV-xxx（不同模块）\n"
        "  违规：[BLUEPRINT]=MOD-GOV_error_pattern_library,\n"
        "        [A_module]=MOD-GOV-error_pattern_library（同模块双拼写）\n"
        "  逃生：在 added 行添加 # noqa: blueprint-amodule-cross-check <reason>\n"
        + "\n".join(violations)
        + "\n-> 统一两头部 module_id 拼写（建议用 DASH 格式与 [A_module] 一致）"
    )


def make_blueprint_amodule_cross_check_gate() -> GateSpec:
    """构造 [BLUEPRINT] vs [A_module] 交叉校验门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-AMODULE-CROSS-CHECK", priority=119)。
        priority=119——在 STASH-ACCUMULATION(118) 之后（117 被 ISSUE-RESOLVED-INTEGRITY 占用）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "BLUEPRINT-AMODULE-CROSS-CHECK")
            if not is_test_exempt(f)
        ]
        if not py_files:
            return True, ""

        violations = _check_cross_consistency(gateway, py_files)
        if violations:
            logger.error(
                "BLUEPRINT-AMODULE-CROSS-CHECK gate block: %d violation(s)",
                len(violations),
            )
            return _format_violations(violations)
        return True, ""

    return GateSpec(
        gate_id="BLUEPRINT-AMODULE-CROSS-CHECK",
        priority=119,
        check=_check,
    )
