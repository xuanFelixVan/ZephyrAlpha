# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.ch_final_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增/修改 .py 文件中直接调用 ch_writer.query() 时阻断 commit（应改用 ch_reader.query() 自动注入 FINAL）; ch_reader.py/ch_writer.py 豁免; tests/ 豁免; 新增文件全文件 AST 检测; 修改文件检测 staged diff 新增行文本模式; AST/git 异常 fail-open
# [MODIFY-GUARD] gate_id="CH-FINAL-GATE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO/git 异常降级为 fail-open（passed=True，logger.warning）; 检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_ch_final_gate.py
# [A_module] module_id=MOD-GOV-ch_final_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_final_gate.py — ch_writer.query() 直接调用阻断门禁（CH-FINAL-GATE，裁定 #ARCH-CH-007 B5）

检测 staged .py 文件中是否直接调用 ch_writer.query()。
违反裁定 #ARCH-CH-007：所有 ClickHouse 查询应走 ch_reader.query() 自动注入 FINAL。

病根（第一性原理）
-----------------
ReplacingMergeTree 的去重是异步的（后台 merge 时才去重）。
查询时需加 FINAL 关键字强制去重。100% AI 开发模式下，AI 不会主动加 FINAL。
ch_reader.query() 自动注入 FINAL，但 AI 可能绕过 ch_reader 直接用 ch_writer.query()。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁：
  1. 新增文件(A)：全文件 AST 检测 ch_writer.query() 调用
  2. 修改文件(M)：检测 staged diff 新增行中的文本模式
  3. ch_reader.py / ch_writer.py 豁免（基础设施）
  4. tests/ 豁免

Usage::

    from zephyr.gov_enforcement.commit_gates.ch_final_gate import make_ch_final_gate

    registry.register(make_ch_final_gate())
"""

from __future__ import annotations

import ast
import logging
import os
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_ch_final_gate"]

# ch_writer.query() 文本模式（用于 diff 新增行检测，覆盖常见别名 ch_writer / _chw）
_QUERY_CALL_PATTERN = re.compile(r'\b(ch_writer|_chw)\s*\.\s*query\s*\(')

# 基础设施文件豁免（文件名后缀）——ch_reader 内部调用 ch_writer.query 是正常的
_INFRA_EXEMPT_SUFFIXES = ("ch_reader.py", "ch_writer.py")


def _collect_ch_writer_aliases(tree: ast.AST) -> set[str]:
    """收集 AST 中 ch_writer 的 import 别名。"""
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "ch_writer":
                    aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith(".ch_writer") or alias.name == "ch_writer":
                    aliases.add(alias.asname or alias.name.split(".")[-1])
    return aliases


def _find_query_calls(tree: ast.AST, aliases: set[str]) -> list[int]:
    """检测 AST 中 alias.query() 调用，返回行号列表。"""
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "query" and isinstance(node.func.value, ast.Name):
                if node.func.value.id in aliases:
                    lines.append(node.lineno)
    return lines


def _is_infra_exempt(rel_path: str) -> bool:
    """检查文件是否为基础设施豁免（ch_reader.py / ch_writer.py）。"""
    normalized = rel_path.replace("\\", "/")
    return any(normalized.endswith(s) for s in _INFRA_EXEMPT_SUFFIXES)


def _check_new_file(abs_path: str, rel_path: str) -> str | None:
    """新增文件全文件 AST 检测，返回违规描述或 None。"""
    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        logger.warning("CH-FINAL-GATE skip %s: 读取失败(%s)", abs_path, e)
        return None
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning("CH-FINAL-GATE skip %s: AST 解析失败(%s)", abs_path, e)
        return None
    aliases = _collect_ch_writer_aliases(tree)
    if not aliases:
        return None
    lines = _find_query_calls(tree, aliases)
    if lines:
        return f"{rel_path}:L{lines[0]} (ch_writer.query → ch_reader.query)"
    return None


def _check_modified_file(gateway, rel_path: str) -> str | None:
    """修改文件检测 staged diff 新增行中的 ch_writer.query 文本模式。"""
    try:
        diff_content = gateway._run_git(
            ["git", "diff", "--cached", "--unified=0", "--", rel_path]
        )
        if diff_content.returncode != 0:
            return None
        added_lines = [
            line[1:] for line in diff_content.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
    except Exception:
        return None
    for line in added_lines:
        if _QUERY_CALL_PATTERN.search(line):
            return f"{rel_path} (modified: 新增 ch_writer.query 调用)"
    return None


def _get_staged_py_files(gateway) -> list[str]:
    """获取 staged added/modified .py 文件（过滤 tests/ 和基础设施豁免）。"""
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if diff_result.returncode != 0:
            logger.warning("CH-FINAL-GATE fail-open: git diff 失败(rc=%d)", diff_result.returncode)
            return []
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning("CH-FINAL-GATE fail-open: git diff 异常(%s: %s)", type(e).__name__, e)
        return []
    return [
        f.replace("\\", "/") for f in staged
        if f.endswith(".py") and not is_test_exempt(f) and not _is_infra_exempt(f)
    ]


def _get_wt_root(gateway) -> str:
    """获取 worktree root 路径。"""
    try:
        toplevel = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
        return toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:
        return str(gateway.project_root)


def _get_added_set(gateway) -> set[str]:
    """获取 staged 新增(A)文件集合。"""
    try:
        added_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
        )
        return set(added_result.stdout.strip().splitlines()) if added_result.returncode == 0 else set()
    except Exception:
        return set()


def _scan_violations(gateway, py_files: list[str], added_set: set[str], wt_root: str) -> list[str]:
    """逐文件检测 ch_writer.query() 调用，返回违规描述列表。"""
    violations: list[str] = []
    for rel_path in py_files:
        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        v = _check_new_file(abs_path, rel_path) if rel_path in added_set else _check_modified_file(gateway, rel_path)
        if v:
            violations.append(v)
    return violations


def make_ch_final_gate() -> GateSpec:
    """构造 ch_writer.query() 直接调用阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CH-FINAL-GATE", priority=37)。
        priority=37——紧邻 CH-BATCH-SIZE(36)，同为 ClickHouse 相关门禁。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _get_staged_py_files(gateway)
        if not py_files:
            return True, ""
        wt_root = _get_wt_root(gateway)
        added_set = _get_added_set(gateway)
        violations = _scan_violations(gateway, py_files, added_set, wt_root)
        if not violations:
            return True, ""
        detail = "; ".join(violations[:5])
        return False, (
            f"直接调用 ch_writer.query() 应改用 ch_reader.query() 以自动注入 FINAL"
            f"（裁定 #ARCH-CH-007）: {detail}"
        )

    return GateSpec(gate_id="CH-FINAL-GATE", check=_check, priority=37)
