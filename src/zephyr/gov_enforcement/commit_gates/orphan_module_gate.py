# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.orphan_module_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 硬阻断——staged 新增 .py 模块在代码库中无任何 import 引用时阻断 commit（死代码，违反"新AI可发现性"原则）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；只检测新增文件（diff-filter=A）；入口文件豁免（__main__/__init__/main/conftest/scripts/ 含 __main__ 块）；subprocess git grep 检测引用；超时/异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="ORPHAN-MODULE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git grep 超时/异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_orphan_module_gate.py
# [A_module] module_id=MOD-GOV-orphan_module_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""orphan_module_gate.py — 孤儿模块（无 import 引用）阻断门禁（ORPHAN-MODULE）

检测 staged 新增 .py 模块在代码库中无任何 import 引用——死代码 on creation，
违反"新AI可发现性"原则（新模块必须被 import 才能被发现和使用）。

病根（第一性原理）
-----------------
新 AI 创建模块后忘记在调用方 import，导致：
  1. 模块无人调用（死代码 on creation）
  2. 后续 AI grep 不到引用，可能重复实现相同功能
  3. 模块依赖图断裂，depgraph 工具无法发现
铁律要求新模块必须有 import 引用（入口文件豁免）。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 计算 staged 新增 .py 模块的 dotted import path 和 short name
  2. 入口文件豁免：``__main__.py`` / ``__init__.py`` / ``main.py`` / ``conftest.py``
     或路径含 ``scripts/`` / ``bin/``，或文件含 ``if __name__ == "__main__":`` 块
  3. ``git grep`` 搜索代码库 ``src/**/*.py`` 是否含 ``import {short_name}`` /
     ``from .* import {short_name}`` / ``from {module_path}``
  4. 0 匹配 -> 孤儿模块 -> 违规

设计权衡
--------
1. **只检测新增文件**：只查 staged 新文件是否被 import。
2. **subprocess git grep**：用 git grep 而非 Python walk——git grep 快（C 实现），
   且只搜 git 追踪的文件（不搜 .gitignore 排除的文件）。
3. **fail-open on grep error**：git grep 超时/异常不阻断，环境异常非违规。
4. **入口文件豁免**：``__main__.py`` 等入口文件本就不被 import。
5. **priority=89**：在 EMPTY-HANDLER(84) 之后、DOC-REF-BROKEN(88) 之前。

Usage::

    from zephyr.gov_enforcement.commit_gates.orphan_module_gate import make_orphan_module_gate

    registry.register(make_orphan_module_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import ast
import logging
import os
import subprocess

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_orphan_module_gate"]

# 入口文件名（不检测孤儿）
_ENTRY_FILENAMES = frozenset({"__main__.py", "__init__.py", "main.py", "conftest.py"})

# 入口路径片段
_ENTRY_PATH_FRAGMENTS = ("scripts/", "bin/")

# git grep 超时（秒）
_GREP_TIMEOUT = 30


def _is_entry_point(rel_path: str, content: str) -> bool:
    """判断文件是否是入口文件（入口文件本就不被 import，豁免孤儿检测）。

    Args:
        rel_path: 相对路径（正斜杠）。
        content: 文件内容。

    Returns:
        True 表示是入口文件。
    """
    fname = os.path.basename(rel_path)
    if fname in _ENTRY_FILENAMES:
        return True
    if any(frag in rel_path for frag in _ENTRY_PATH_FRAGMENTS):
        return True
    # 含 if __name__ == "__main__": 块
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            # if __name__ == "__main__":
            if (isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == "__main__"):
                return True
    return False


def _compute_module_path(rel_path: str) -> tuple[str, str]:
    """从相对路径计算 dotted module path 和 short name。

    ``src/zephyr/governance/foo.py`` -> ("zephyr.governance.foo", "foo")
    ``src/zephyr/governance/pkg/__init__.py`` -> ("zephyr.governance.pkg", "pkg")

    Args:
        rel_path: 相对路径（正斜杠）。

    Returns:
        (module_path, short_name) 元组。
    """
    path = rel_path
    # 去 src/ 前缀
    if path.startswith("src/"):
        path = path[len("src/"):]
    # 去 .py
    if path.endswith(".py"):
        path = path[:-3]
    # __init__.py -> 取目录名作为模块名
    if path.endswith("/__init__"):
        path = path[: -len("/__init__")]
    module_path = path.replace("/", ".")
    short_name = os.path.basename(rel_path)
    if short_name.endswith(".py"):
        short_name = short_name[:-3]
    if short_name == "__init__":
        short_name = os.path.basename(os.path.dirname(rel_path))
    return module_path, short_name


def _collect_staged_new_py_files(gateway) -> "tuple[list[str], str] | None":
    """获取 staged 新增 .py 文件（tests/ 豁免）的绝对路径列表 + worktree root。

    Returns:
        None=fail-open（调用方应返回 pass）；([], "")=无文件待检；
        (abs_files, wt_root)=待检文件列表与 worktree 根目录。
    """
    # 1. 获取 staged 新增 .py 文件
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "ORPHAN-MODULE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        staged_new = diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning(
            "ORPHAN-MODULE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True
        )
        return None

    # 2. 过滤 .py 文件 + tests/ 豁免
    new_py_files = [
        f.replace("\\", "/") for f in staged_new
        if f.endswith(".py") and not is_test_exempt(f)
    ]
    if not new_py_files:
        return [], ""

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
    return abs_files, wt_root


def _detect_orphans(gateway, abs_files: list[str], wt_root: str) -> "list[str] | None":
    """检测孤儿模块列表。None=fail-open（调用方应返回 pass）。

    对每个文件：读内容 → 入口豁免 → 计算 module path → git grep 搜索 import 引用 →
    exit 0 有其他文件引用=非孤儿；exit 1 无匹配=孤儿；其他=错误 fail-open。
    """
    violations: list[str] = []
    for abs_path in abs_files:
        rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
        try:
            content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
        except OSError as e:
            logger.warning(
                "ORPHAN-MODULE gate skip file %s: 读取失败(%s: %s)。",
                abs_path, type(e).__name__, e,
            )
            continue

        # 入口文件豁免
        if _is_entry_point(rel_name, content):
            continue

        module_path, short_name = _compute_module_path(rel_name)
        if not module_path or not short_name:
            continue

        # git grep 搜索 import 引用
        # pattern: import {short_name} | from .* import {short_name} | from {module_path}
        # P13 fix (2026-07-13): 添加 import {module_path} 模式，匹配
        # `import <full.dotted.path> as <alias>` 形式（原 pattern 只匹配
        # `import {short_name}` 和 `from ... import {short_name}`，
        # 漏检 `import zephyr.pkg.mod as mod` 这种常见写法）
        pattern = (
            rf"import {short_name}\b|"
            rf"from .* import {short_name}\b|"
            rf"from {module_path}\b|"
            rf"import {module_path}\b"
        )
        try:
            grep_result = gateway._run_git(
                ["git", "grep", "-l", "-E", pattern, "--", "src/**/*.py"],
                cwd=wt_root,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "ORPHAN-MODULE gate fail-open: git grep 超时(%ds)，检测器失效。",
                _GREP_TIMEOUT,
            )
            return None
        except Exception as e:
            logger.warning(
                "ORPHAN-MODULE gate fail-open: git grep 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return None

        # git grep exit 0 = 有匹配；exit 1 = 无匹配；其他 = 错误
        if grep_result.returncode == 0:
            # 有匹配——但需排除文件自身（grep 可能匹配到 staged 文件本身）
            matched_files = [
                f for f in grep_result.stdout.strip().splitlines() if f
            ]
            # 过滤掉自身
            others = [f for f in matched_files if f != rel_name and f != rel_name.replace("/", os.sep)]
            if others:
                continue  # 有其他文件引用，非孤儿
            # 仅自身匹配 -> 孤儿
        elif grep_result.returncode == 1:
            # 无匹配 -> 孤儿
            pass
        else:
            # git grep 错误（exit != 0 且 != 1）
            logger.warning(
                "ORPHAN-MODULE gate fail-open: git grep 错误(rc=%d)：%s",
                grep_result.returncode,
                (grep_result.stderr or "")[:200],
            )
            return None

        violations.append(rel_name)
    return violations


def make_orphan_module_gate() -> GateSpec:
    """构造孤儿模块（无 import 引用）阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="ORPHAN-MODULE", priority=89)。
        priority=89——在 EMPTY-HANDLER(84) 之后、DOC-REF-BROKEN(88) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        collected = _collect_staged_new_py_files(gateway)
        if collected is None:
            return True, ""
        abs_files, wt_root = collected
        if not abs_files:
            return True, ""
        violations = _detect_orphans(gateway, abs_files, wt_root)
        if violations is None:
            return True, ""
        if violations:
            detail = "; ".join(violations[:5])
            return False, (
                f"孤儿模块在代码库中无任何 import 引用"
                f"（死代码，违反新AI可发现性）: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="ORPHAN-MODULE", check=_check, priority=89)
