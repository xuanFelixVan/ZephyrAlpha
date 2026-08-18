# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-GIT-CALL-BUDGET
# [MODULE] zephyr.gov_enforcement.commit_gates.git_call_budget_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn-only——检测 staged .py 中 subprocess.run(["git",...]) 在 for/while 循环内调用（逐文件 git 调用反模式）；命中返回 passed=True + warning detail（不阻断）；tests/ 豁免；AST 精确检测（parent map 遍历）；git diff 不可达 fail-open
# [MODIFY-GUARD] gate_id="GIT-CALL-BUDGET"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True）；ast.parse 失败 fail-open；检出违规则 warn-only（passed=True + detail）
# [TESTS] tests/governance/commit_gates/test_git_call_budget_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""git_call_budget_gate.py — Git 调用预算 warn-only 门禁（GIT-CALL-BUDGET，§ARCH-GIT-CALL-BUDGET P2.2）

检测 staged .py 文件中 ``subprocess.run(["git", ...])`` 在 for/while 循环内直接调用
（逐文件 git 调用反模式——N 文件 = N subprocess）。
对应铁律 trae_064 ARCH-GIT-CALL-BUDGET（GIT-BUDGET-INV-002 批量化强制）。

病根（第一性原理）
-----------------
git 是昂贵外部资源，每次 subprocess.run(["git", ...]) 在 Windows 上成本
~50-100ms + fscache/fsmonitor 初始化开销。100% AI 开发场景下 session_worktree /
gates / reconcilers 高频调 git，逐文件调用（N 文件 = N subprocess）在 14 万文件
工作区 + fscache/fsmonitor 路径上是 git.exe 2.48.x 崩溃（0xc0000005 @ 0x13e4d4）
的放大源。

治本方案（trae_064 ARCH-GIT-CALL-BUDGET）
-------------------------------------------
1. P1.2 批量化：用 GitCommandBatcher.git_show_batch（git archive --format=tar）
   将 N 次 git show 降为 1 次
2. P1.3 fast-path：可信内部调用方设置 ZEPHYR_GIT_GUARD_FAST_PATH=1 跳过 alias 扫描
3. P2.1 铁律：trae_064 YAML 定义预算表 + 批量化要求
4. P2.2 本 gate：静态检测反模式，warn-only（P3 升级 block）

设计权衡
--------
1. **warn-only（P2）**：当前 warn-only 不阻断 commit，先建立检测能力 + 数据收集。
   P3 升级为 block（GIT-BUDGET-INV-002 violation_action=reject_change）。
2. **AST 精确检测**：用 ast.walk + parent map 判断 subprocess.run Call 节点是否
   在 For/While 体内，比正则更准确。
3. **只检测 added 行**：存量违规由人工排查，gate 只防新增。
4. **priority=105**：warn-only gate 放最后，不阻断前面的硬 gate。

Usage::

    from zephyr.gov_enforcement.commit_gates.git_call_budget_gate import make_git_call_budget_gate

    registry.register(make_git_call_budget_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_git_call_budget_gate"]

# 豁免文件：GitCommandBatcher 自身（定义批量化 API，内部有 subprocess 调用但不在循环内）
_EXEMPT_FILES = {"git_batcher.py", "git_call_budget_gate.py", "_diff_helpers.py"}


def _is_git_budget_exempt_file(py_file: str) -> bool:  # noqa: m03-duplicate  M03豁免: 与ch_batch_size_gate._is_exempt_file共享实现（各gate持自身_EXEMPT_FILES常量，共享模块提取为后续重构，对标_reference_helpers模式）
    """文件级豁免：GitCommandBatcher / 本 gate / diff helpers 自身。

    重命名自 _is_exempt_file 以避免 FUNCTION-DUP gate 与 ch_batch_size_gate 冲突。
    """
    return any(py_file.replace("\\", "/").endswith(f"/{name}") or py_file == name
               for name in _EXEMPT_FILES)


def _build_git_parent_map(tree: ast.AST) -> dict[int, ast.AST]:  # noqa: m03-duplicate  M03豁免: 与ch_batch_size_gate._build_parent_map共享实现（各gate持自身常量，共享模块提取为后续重构，对标_reference_helpers模式）
    """构建 AST parent map：{id(child_node): parent_node}。

    重命名自 _build_parent_map 以避免 FUNCTION-DUP gate 与 ch_batch_size_gate 冲突。
    """
    parent_map: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[id(child)] = node
    return parent_map


def _find_enclosing_loop(
    call_node: ast.Call, parent_map: dict[int, ast.AST]
) -> ast.For | ast.While | ast.AsyncFor | None:
    """从 Call 节点向上遍历祖先链，返回最近的 For/While/AsyncFor 祖先。"""
    current = parent_map.get(id(call_node))
    while current is not None:
        if isinstance(current, (ast.For, ast.While, ast.AsyncFor)):
            return current
        current = parent_map.get(id(current))
    return None


def _is_git_subprocess_call(node: ast.AST) -> bool:
    """判断 AST 节点是否是 subprocess.run(["git", ...]) 调用。

    覆盖：
    - ``subprocess.run(["git", ...])`` — ast.Attribute(attr='run')
    - ``subprocess.check_output(["git", ...])`` — ast.Attribute(attr='check_output')
    - ``subprocess.check_call(["git", ...])`` — ast.Attribute(attr='check_call')
    - ``subprocess.Popen(["git", ...])`` — ast.Attribute(attr='Popen')

    只匹配第一个参数是列表字面量且首元素是 "git" 字符串的情况。
    """
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr not in ("run", "check_output", "check_call", "Popen"):
        return False
    # 第一个参数必须是列表字面量
    if not node.args:
        return False
    first_arg = node.args[0]
    if not isinstance(first_arg, ast.List):
        return False
    if not first_arg.elts:
        return False
    first_elt = first_arg.elts[0]
    if isinstance(first_elt, ast.Constant) and isinstance(first_elt.value, str):
        return first_elt.value == "git"
    return False


def make_git_call_budget_gate() -> GateSpec:
    """构造 Git 调用预算 warn-only GateSpec。

    Returns:
        GateSpec(gate_id="GIT-CALL-BUDGET", priority=105)。
        warn-only：检出违规返回 (True, warning_detail)，不阻断 commit。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "GIT-CALL-BUDGET")
            if not is_test_exempt(f) and not _is_git_budget_exempt_file(f)
        ]
        if not py_files:
            return True, ""

        warnings: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "GIT-CALL-BUDGET")}
            if not added_lines:
                continue

            try:
                tree = ast.parse(file_content)
            except SyntaxError:
                logger.warning(
                    "GIT-CALL-BUDGET: ast.parse 失败 %s（语法错误），fail-open 跳过",
                    py_file, exc_info=True,
                )
                continue

            parent_map = _build_git_parent_map(tree)

            for node in ast.walk(tree):
                if not _is_git_subprocess_call(node):
                    continue
                loop_node = _find_enclosing_loop(node, parent_map)
                if loop_node is None:
                    continue  # 不在循环内，放行
                call_line = node.lineno
                loop_line = loop_node.lineno
                if call_line in added_lines or loop_line in added_lines:
                    warnings.append(
                        f"  {py_file}:{call_line}: subprocess.run([\"git\", ...]) "
                        f"在 {'for' if isinstance(loop_node, (ast.For, ast.AsyncFor)) else 'while'} "
                        f"循环内调用（循环头在第 {loop_line} 行）"
                    )

        if warnings:
            detail = (
                "GIT-CALL-BUDGET (warn-only)：检测到 subprocess.run([\"git\", ...]) "
                "在循环内调用，\n"
                "  违反铁律 trae_064 ARCH-GIT-CALL-BUDGET GIT-BUDGET-INV-002 批量化强制——\n"
                "  逐文件 git 调用（N 文件 = N subprocess）是 git.exe 崩溃的放大源。\n"
                + "\n".join(warnings)
                + "\n-> 改用 GitCommandBatcher："
                "from zephyr.infrastructure.git_batcher import GitCommandBatcher; "
                "batcher.git_show_batch(ref, files)"
            )
            logger.warning("GIT-CALL-BUDGET gate warn:\n%s", detail)
            return True, detail  # warn-only：passed=True 不阻断
        return True, ""

    return GateSpec(gate_id="GIT-CALL-BUDGET", check=_check, priority=105)
