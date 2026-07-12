# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.function_dup_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 文件中顶层函数在**同目录其他文件**已存在相同 name + body hash 实现时阻断 commit（重复代码）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A）；只比顶层函数（不比方法）；scope 限同目录（避免扫描全代码库）；AST/subprocess 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="FUNCTION-DUP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/subprocess 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_function_dup_gate.py
# [A_module] module_id=MOD-GOV-function_dup_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""function_dup_gate.py — 重复函数实现阻断门禁（FUNCTION-DUP）

检测 staged 新增 .py 文件中顶层函数是否在**同目录其他文件**中已存在相同
name + body hash 的实现——重复代码违反 DRY 原则，应扩展现有函数而非复制。

病根（第一性原理）
-----------------
新 AI 创建函数时可能复制同目录其他文件的实现：
  1. 同名同实现（完全复制粘贴）—— 明显重复
  2. 同名不同实现 —— 不算重复（可能是有意重载，跳过）
  3. 不同名同实现 —— 难检测（需语义分析），本 gate 不覆盖
重复代码让后续维护要改多处，违反 SSoT 原则。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. AST 解析 staged 新增 .py 文件，提取顶层 FunctionDef/AsyncFunctionDef
  2. 计算每个函数的 body hash（排除 docstring 后 ast.unparse(body)）
  3. 扫描同目录其他 .py 文件，找同名函数，比较 body hash
  4. hash 相同 -> 重复 -> 违规

设计权衡
--------
1. **只检测顶层函数**：方法（类内函数）可能是有意重载，不检测。
2. **scope 限同目录**：避免扫描全代码库（性能）。同目录重复最常见（同模块
   内复制粘贴），跨目录重复由其他 gate（如 SSOT-REDEFINITION）覆盖。
3. **body hash 而非全文比较**：ast.unparse 标准化空白/注释，hash 比较稳健。
4. **fail-open on AST error**：语法错误文件不阻断。
5. **priority=90**：在 DOC-REF-BROKEN(88) 之后（最后执行，重复检测最贵）。

Usage::

    from zephyr.governance.commit_gates.function_dup_gate import make_function_dup_gate

    registry.register(make_function_dup_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_function_dup_gate"]


def _function_body_hash(func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """计算函数体的归一化 hash（排除 docstring）。

    Args:
        func: ast.FunctionDef 或 ast.AsyncFunctionDef 节点。

    Returns:
        sha256 hash 前 16 字符（hex）。
    """
    # 过滤掉 docstring（第一个 Expr + Constant str）
    body_stmts: list[ast.stmt] = []
    for stmt in func.body:
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)):
            continue  # docstring
        body_stmts.append(stmt)
    # unparse body 语句拼接
    try:
        normalized = "\n".join(ast.unparse(s) for s in body_stmts)
    except Exception:
        # unparse 失败时用空字符串（hash 不会匹配，跳过该函数）
        normalized = ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _extract_top_level_functions(tree: ast.AST) -> dict[str, str]:
    """提取 AST 中所有顶层函数的 name -> body_hash 映射。

    Args:
        tree: 已解析的 AST。

    Returns:
        dict[str, str]：函数名 -> body hash（前 16 字符）。
    """
    result: dict[str, str] = {}
    for node in tree.body if hasattr(tree, "body") else []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result[node.name] = _function_body_hash(node)
    return result


def _scan_sibling_functions(abs_path: str, exclude_path: str) -> dict[str, tuple[str, str]]:
    """扫描同目录其他 .py 文件的顶层函数。

    Args:
        abs_path: 新文件的绝对路径（用于确定目录）。
        exclude_path: 要排除的文件绝对路径（新文件自身）。

    Returns:
        dict[func_name, (other_file_abs_path, body_hash)]。
    """
    directory = os.path.dirname(abs_path)
    siblings: dict[str, tuple[str, str]] = {}
    try:
        entries = os.listdir(directory)
    except OSError:
        return siblings
    for entry in entries:
        if not entry.endswith(".py"):
            continue
        sibling_path = os.path.join(directory, entry)
        if os.path.abspath(sibling_path) == os.path.abspath(exclude_path):
            continue  # 排除自身
        try:
            content = open(sibling_path, "r", encoding="utf-8", errors="replace").read()
            tree = ast.parse(content, filename=sibling_path)
        except (OSError, SyntaxError) as e:
            logger.warning(
                "FUNCTION-DUP gate skip sibling %s: 解析失败(%s: %s)。",
                sibling_path, type(e).__name__, e,
            )
            continue
        funcs = _extract_top_level_functions(tree)
        for fname, fhash in funcs.items():
            if fname not in siblings:
                siblings[fname] = (sibling_path, fhash)
    return siblings


def make_function_dup_gate() -> GateSpec:
    """构造重复函数实现阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="FUNCTION-DUP", priority=90)。
        priority=90——在 DOC-REF-BROKEN(88) 之后（最后执行，重复检测最贵）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 新增 .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "FUNCTION-DUP gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged_new = diff_result.stdout.strip().splitlines()
        except Exception as e:
            logger.warning(
                "FUNCTION-DUP gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        # 2. 过滤 .py 文件 + tests/ 豁免
        new_py_files = [
            f.replace("\\", "/") for f in staged_new
            if f.endswith(".py") and not is_test_exempt(f)
        ]
        if not new_py_files:
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(
                ["git", "rev-parse", "--show-toplevel"]
            )
            if toplevel_result.returncode == 0:
                wt_root = toplevel_result.stdout.strip()
            else:
                wt_root = str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 4. 解析为绝对路径
        abs_files = []
        for rel in new_py_files:
            if os.path.isabs(rel):
                abs_files.append(rel)
            else:
                abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
        abs_files = [f for f in abs_files if os.path.isfile(f)]
        if not abs_files:
            return True, ""

        # 5. AST 检测：同目录重复函数
        all_violations: list[str] = []
        for abs_path in abs_files:
            try:
                content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                logger.warning(
                    "FUNCTION-DUP gate skip file %s: 读取失败(%s: %s)。",
                    abs_path, type(e).__name__, e,
                )
                continue

            try:
                tree = ast.parse(content, filename=abs_path)
            except SyntaxError as e:
                logger.warning(
                    "FUNCTION-DUP gate skip file %s: AST 解析失败(%s: %s)，检测器失效。",
                    abs_path, type(e).__name__, e,
                )
                continue

            new_funcs = _extract_top_level_functions(tree)
            if not new_funcs:
                continue  # 无顶层函数

            # 扫描同目录其他 .py 文件
            siblings = _scan_sibling_functions(abs_path, abs_path)
            if not siblings:
                continue  # 同目录无其他 .py 或无函数

            rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
            for fname, fhash in new_funcs.items():
                if fname in siblings:
                    other_path, other_hash = siblings[fname]
                    if fhash == other_hash and fhash:  # hash 相同且非空
                        other_rel = os.path.relpath(other_path, wt_root).replace("\\", "/")
                        all_violations.append(
                            f"重复函数 {fname} 在 {other_rel} 已存在相同实现"
                            f"（hash={fhash}，新文件 {rel_name}）"
                        )

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, detail
        return True, ""

    return GateSpec(gate_id="FUNCTION-DUP", check=_check, priority=90)
