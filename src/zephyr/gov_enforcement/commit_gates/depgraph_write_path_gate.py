# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.depgraph_write_path_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 read_only=False/superuser=True/allow_edge_delete=True 且文件不在白名单时阻断commit(passed=False); tests/豁免; docstring/注释/import行豁免; git diff不可达fail-open; 检出违规则fail-closed
# [MODIFY-GUARD] gate_id="DEPGRAPH-WRITE-PATH"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_depgraph_write_path_gate.py
# [TTL] permanent
"""depgraph_write_path_gate.py — depgraph 写入路径白名单门禁（DEPGRAPH-WRITE-PATH）

裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: 角色分级访问控制的技术执行层

检测 staged .py 文件 added 行中的 read_only=False / superuser=True / allow_edge_delete=True。
这些参数授予 depgraph 写入权限，仅白名单脚本可用。

白名单（裁定#ARCH-DEPGRAPH_ACCESS_CONTROL，2026-07-17 扩展）:
  - scripts/governance/apply_depgraph.py        — depgraph 修改唯一合法 CLI
  - scripts/governance/generate_project_depgraph.py — 全量重建
  - scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py — YAML→DB 同步
  - scripts/governance/sync_panorama_module.py  — panorama 同步（含 path-tree 段）
  - scripts/governance/generate_project_path_tree.py — arch_directory_tree 表写入器（新增）
  - scripts/governance/_shared/constants.py      — 连接 wrapper（传递参数）
  - src/zephyr/governance/depgraph_schema.py     — 连接函数定义（参数声明）

白名单扩展规则（治本，2026-07-17 明确化）：
  所有直接写 depgraph 表（nodes/edges/arch_directory_tree 等）的脚本必须加入白名单。
  扩展三步：(a) 脚本传 read_only=False (b) 更新本白名单 + 错误信息 (c) 更新
  architecture_issue_registry.yaml 中 #ARCH-DEPGRAPH_ACCESS_CONTROL 裁定文档。

设计权衡
--------
1. **只检测 added 行**：存量调用由 Phase 5 排查，gate 只防新增。
2. **diff-based**：与 bare_sql_gate 一致的检测模式。
3. **正则匹配**：覆盖 read_only=False / superuser=True / allow_edge_delete=True。
4. **priority=100**：在 META-TESTS-COVERAGE(99) 之后、CAP-CONSISTENCY(101) 之前，检测 depgraph 写入路径白名单。

Usage::

    from zephyr.gov_enforcement.commit_gates.depgraph_write_path_gate import make_depgraph_write_path_gate

    registry.register(make_depgraph_write_path_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _is_exempt_line,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_depgraph_write_path_gate"]

# depgraph 写入权限参数模式
# 匹配 read_only=False / superuser=True / allow_edge_delete=True
_WRITE_PARAM_RE = re.compile(
    r"(read_only\s*=\s*False|superuser\s*=\s*True|allow_edge_delete\s*=\s*True)"
)

# 白名单文件（相对仓库根，正斜杠）
# 治本（2026-07-17）：新增 generate_project_path_tree.py（arch_directory_tree 表写入器）
_WHITELIST: frozenset[str] = frozenset({
    "scripts/governance/apply_depgraph.py",
    "scripts/governance/generate_project_depgraph.py",
    "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
    "scripts/governance/_shared/constants.py",
    "scripts/governance/sync_panorama_module.py",
    "scripts/governance/generate_project_path_tree.py",
    "src/zephyr/governance/depgraph_schema.py",
})


def _is_whitelisted(file_path: str) -> bool:
    """判断文件是否在 depgraph 写入路径白名单中。"""
    normalized = file_path.replace("\\", "/")
    return normalized in _WHITELIST


# Gate 自身文件路径——豁免自循环检测
# 治本（2026-07-17）：gate 自身的错误信息/docstring/注释中自然包含 "read_only=False"
# 等检测模式字符串（用于提示用户），若不豁免自身，gate 会检测自己的字符串字面量
# 导致自循环阻断。语义上 gate 检测的是「代码调用」，不是「字符串字面量」。
_SELF_FILE = "src/zephyr/gov_enforcement/commit_gates/depgraph_write_path_gate.py"


def _is_self(file_path: str) -> bool:
    """判断文件是否是本 gate 自身（豁免自循环）。"""
    normalized = file_path.replace("\\", "/")
    return normalized == _SELF_FILE


def make_depgraph_write_path_gate() -> GateSpec:
    """构造 depgraph 写入路径白名单 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="DEPGRAPH-WRITE-PATH", priority=100)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "DEPGRAPH-WRITE-PATH")
            if not is_test_exempt(f) and not _is_whitelisted(f) and not _is_self(f)
        ]
        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            docstring_lines = (
                _extract_docstring_lines(file_content) if file_content else set()
            )
            for line_no, content in _get_added_lines(gateway, py_file, "DEPGRAPH-WRITE-PATH"):
                if line_no in docstring_lines or _is_exempt_line(content):
                    continue
                if _WRITE_PARAM_RE.search(content):
                    violations.append(f"  {py_file}:{line_no}: {content.strip()}")
        if violations:
            detail = (
                "DEPGRAPH-WRITE-PATH：检测到 depgraph 写入权限参数\n"
                "  (read-only disabled / superuser / edge-delete enabled)，\n"
                "  但文件不在白名单中。裁定#ARCH-DEPGRAPH_ACCESS_CONTROL 规定\n"
                "  仅以下文件可使用写入权限：\n"
                "    - scripts/governance/apply_depgraph.py\n"
                "    - scripts/governance/generate_project_depgraph.py\n"
                "    - scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py\n"
                "    - scripts/governance/_shared/constants.py\n"
                "    - scripts/governance/sync_panorama_module.py\n"
                "    - scripts/governance/generate_project_path_tree.py\n"
                "    - src/zephyr/governance/depgraph_schema.py\n"
                "  白名单扩展规则：所有直接写 depgraph 表（nodes/edges/arch_directory_tree\n"
                "  等）的脚本必须加入白名单，扩展三步——(a) 脚本传 read_only=False\n"
                "  (b) 更新本白名单+错误信息 (c) 更新 architecture_issue_registry.yaml 裁定文档\n"
                + "\n".join(violations)
                + "\n-> 如需写入 depgraph，请通过 apply_depgraph.py CLI 操作"
            )
            logger.error("DEPGRAPH-WRITE-PATH gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="DEPGRAPH-WRITE-PATH", check=_check, priority=100)
