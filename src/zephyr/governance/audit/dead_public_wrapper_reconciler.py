# [BLUEPRINT] MOD-GOV_DEAD_PUBLIC_WRAPPER_RECONCILER | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | §#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001
# [MODULE] zephyr.governance.audit.dead_public_wrapper_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); stdlib (ast, logging, re, pathlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（src/*.py commit）；reconciler 永不抛异常；warn-only（dead wrapper 不阻断 commit，仅告警供人工审查）
# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _SCAN_DIRS / _EXCLUDE_PREFIXES
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——AST/regex 失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_dead_public_wrapper_reconciler.py
# [A_module] module_id=MOD-GOV_DEAD_PUBLIC_WRAPPER_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)

r"""

dead_public_wrapper_reconciler.py — 死公共 wrapper 自动检测 reconciler.

#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 防复发自动化：post-commit 事件触发，
扫描 src/zephyr/ 下所有 Python 文件，检测"死公共 wrapper"——即公共函数（无下划线
前缀）包裹同名私有函数（_前缀），但无任何外部调用方的 wrapper。

治本动机（第一性原理）
--------------------
#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 手工发现并删除了 5 个死公共 wrapper，但手工扫描遗漏了
workspace_hygiene_reconciler.git_status_porcelain（同样模式，同样零外部调用方）。
本 reconciler 将手工发现升级为持续自动检测，防复发。

检测逻辑
--------
1. AST 解析每个 .py 文件，找模块级/类级 public function + 同 scope 的 _private counterpart
2. 检查 public function body 是否调用 _private counterpart（wrapper pattern）
3. 对每个 wrapper，用 regex 搜索所有 src/zephyr/ .py 文件（排除定义文件本身）
4. 零外部引用 → 死公共 wrapper → warn

排除项
------
- ``__dunder__`` 方法（Python 协议方法，非 wrapper）
- ``make_*`` 函数（工厂模式，非 wrapper）

priority=950（晚于所有其他 reconciler，不干扰）

Usage
-----
::

    from zephyr.governance.audit.dead_public_wrapper_reconciler import (
        make_dead_public_wrapper_reconciler,
    )

    registry.register(make_dead_public_wrapper_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: src/zephyr 下 Python 源码文件
#   fields: rglob *.py（排除 __pycache__）
#   code: _find_dead_public_wrappers L227
# - id: I2
#   name: 全仓调用点文本
#   fields: src/zephyr + scripts + tests 的 .py 文件内容
#   code: search_dirs L266-268
# 层: 算法
# - id: A1
#   name_zh: ① 公私同名函数对发现
#   name_en: _find_function_pairs
#   intro: AST 扫描找同 scope 里 foo 和 _foo 同时存在的函数对
#   desc: 模块级+类级两层扫描；排除 __dunder__ 协议方法与 make_ 工厂函数
#   inputs: I1
#   outputs: 候选 public/private 函数对
# - id: A2
#   name_zh: ② trivial wrapper 判定
#   name_en: _is_trivial_wrapper
#   intro: 剥掉 docstring 后函数体只剩一条转发调用才算 wrapper
#   desc: 仅 1 条真实语句且为 return _foo(...) / _foo(...) / self._foo(...) 形式；多语句/含控制流不算
#   inputs: A1
#   outputs: trivial wrapper 候选
# - id: A3
#   name_zh: ③ 零外部调用方过滤
#   name_en: _find_dead_public_wrappers Phase2/3
#   intro: 用合并正则全仓数调用次数，只剩定义处一次的就是死 wrapper
#   desc: combined regex \b(name1|name2|...)\( 单遍扫描三目录；call_count<=1（仅定义）判死
#   inputs: A2 I2
#   outputs: 死公共 wrapper 列表（file/function/line/scope）
# - id: A4
#   name_zh: ④ reconcile 编排
#   name_en: _reconcile
#   intro: 汇总死 wrapper 清单为 warn 告警，detail 截断防超长
#   desc: 最多列 10 条；warn-only 不阻断 commit；AST/正则异常降级 warn 永不抛出
#   inputs: A3
#   outputs: ReconcileResult(clean/warn)
#   invariant: reconciler 永不抛异常；warn-only
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: warn=检出死公共 wrapper 清单（gate_id=GATE-DEAD-PUBLIC-WRAPPER），clean=无
#   downstream: GitCommitGateway MOD-INF-035
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)

logger = logging.getLogger(__name__)

_GATE_ID = "GATE-DEAD-PUBLIC-WRAPPER"

# priority=950: 晚于所有其他 reconciler（最高 priority=900 remediation_progress）
_PRIORITY = 950

# 扫描目录（相对 project_root）
_SCAN_DIRS = ("src/zephyr",)

# 排除的函数名前缀（这些是 Python 协议方法或工厂模式，非 wrapper）
_EXCLUDE_PREFIXES = ("__", "make_")

# detail 中最多显示的 wrapper 数量（截断防过长）
_MAX_DETAIL_ITEMS = 10


def _find_function_pairs(tree: ast.AST) -> list[dict]:
    """Find public/private function pairs in an AST.

    扫描模块级和类级函数定义，找 ``foo`` + ``_foo`` 同 scope 共存的 pair。

    Args:
        tree: AST tree of a Python file.

    Returns:
        List of dicts with keys: public_name, private_name, public_node,
        private_node, scope, line.
    """
    pairs: list[dict] = []

    # --- 模块级函数 ---
    module_funcs: dict[str, ast.AST] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if not any(name.startswith(p) for p in _EXCLUDE_PREFIXES):
                module_funcs[name] = node

    for name, pub_node in module_funcs.items():
        private_name = "_" + name
        if private_name in module_funcs:
            pairs.append(
                {
                    "public_name": name,
                    "private_name": private_name,
                    "public_node": pub_node,
                    "private_node": module_funcs[private_name],
                    "scope": "module",
                    "line": pub_node.lineno,
                }
            )

    # --- 类级方法 ---
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_funcs: dict[str, ast.AST] = {}
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mname = child.name
                if not any(mname.startswith(p) for p in _EXCLUDE_PREFIXES):
                    class_funcs[mname] = child

        for mname, pub_node in class_funcs.items():
            private_name = "_" + mname
            if private_name in class_funcs:
                pairs.append(
                    {
                        "public_name": mname,
                        "private_name": private_name,
                        "public_node": pub_node,
                        "private_node": class_funcs[private_name],
                        "scope": f"class:{node.name}",
                        "line": pub_node.lineno,
                    }
                )

    return pairs


def _is_trivial_wrapper(node: ast.AST, target_name: str) -> bool:
    """Check if a function is a **trivial wrapper** around target_name.

    ARCH-STAGE4 pattern: public ``foo()`` whose body is ONLY a delegation to
    ``_foo()`` — no complex logic (no if/for/while/try, no multi-statement).

    Accepted body shapes (after stripping docstring):
    - ``return _foo(...)`` / ``return self._foo(...)`` / ``return cls._foo(...)``
    - ``_foo(...)`` / ``self._foo(...)`` (expression statement, no return)

    Args:
        node: The public function's AST node (FunctionDef/AsyncFunctionDef).
        target_name: The private counterpart name (e.g. ``_foo``).

    Returns:
        True if the function body is a trivial delegation to target_name.
    """
    body = node.body

    # Strip docstring (first statement if Expr(Constant(str)))
    real_body = [
        stmt
        for stmt in body
        if not (
            isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)
        )
    ]

    # Trivial wrapper has exactly 1 real statement (the call/return)
    if len(real_body) != 1:
        return False

    stmt = real_body[0]

    # Extract the call expression from return or expr
    if isinstance(stmt, ast.Return):
        call = stmt.value
    elif isinstance(stmt, ast.Expr):
        call = stmt.value
    else:
        return False

    if not isinstance(call, ast.Call):
        return False

    func = call.func
    # Direct call: _foo()
    if isinstance(func, ast.Name) and func.id == target_name:
        return True
    # Attribute call: self._foo() / cls._foo() / obj._foo()
    if isinstance(func, ast.Attribute) and func.attr == target_name:
        return True

    return False


def _find_dead_public_wrappers(project_root: Path) -> list[dict]:
    """Scan src/zephyr/ for dead public wrappers using two-phase detection.

    Phase 1: AST scan of src/zephyr/ to find trivial wrapper candidates
             (public function whose body is ONLY ``return _foo(...)``).
    Phase 2: Single-pass combined-regex caller count across src/zephyr/,
             scripts/, tests/ — if ``func_name(`` appears only once (the
             definition), the wrapper is dead.
    Phase 3: Filter candidates to those with zero external callers.

    Args:
        project_root: Project root directory.

    Returns:
        List of dicts with keys: file, function, line, scope.
    """
    # === Phase 1: Find trivial wrapper candidates ===
    candidates: list[dict] = []

    for scan_dir_rel in _SCAN_DIRS:
        scan_dir = project_root / scan_dir_rel
        if not scan_dir.exists():
            continue

        for py_file in scan_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue

            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(py_file))
            except Exception:  # noqa: BLE001 — 跳过不可解析文件
                continue

            for pair in _find_function_pairs(tree):
                if not _is_trivial_wrapper(pair["public_node"], pair["private_name"]):
                    continue
                candidates.append(
                    {
                        "file": str(py_file.relative_to(project_root)).replace("\\", "/"),
                        "function": pair["public_name"],
                        "line": pair["line"],
                        "scope": pair["scope"],
                    }
                )

    if not candidates:
        return []

    # === Phase 2: Single-pass caller count across all project dirs ===
    # Build a combined regex matching any candidate name followed by (
    # \b ensures _func_name doesn't match (underscore is a word char)
    candidate_names = {c["function"] for c in candidates}
    combined_pattern = re.compile(r"\b(" + "|".join(re.escape(n) for n in candidate_names) + r")\(")

    # Search directories: src/zephyr + scripts + tests
    # (covers production code, scripts, and test calls — but NOT mock patches
    #  which use mock.patch('module.func_name') without trailing ()
    call_counts: dict[str, int] = {name: 0 for name in candidate_names}
    search_dirs = [project_root / d for d in ("src/zephyr", "scripts", "tests")]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for py_file in search_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001 — fail-open
                continue
            for match in combined_pattern.finditer(content):
                name = match.group(1)
                call_counts[name] += 1

    # === Phase 3: Filter to dead wrappers (count <= 1 = only definition) ===
    dead = [c for c in candidates if call_counts[c["function"]] <= 1]

    return dead


def make_dead_public_wrapper_reconciler(gateway: "object") -> ReconcilerSpec:
    """Construct GATE-DEAD-PUBLIC-WRAPPER post-commit dead public wrapper detector.

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。trigger 在
        src/*.py commit 时返回 True；reconcile 扫描死公共 wrapper 并 warn。
    """
    project_root = Path(gateway.project_root)

    def _trigger(committed_files: list[str]) -> bool:
        """Trigger when Python files in src/ are committed."""
        return any(f.startswith("src/") and f.endswith(".py") for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        """Scan for dead public wrappers and warn if found."""
        try:
            dead = _find_dead_public_wrappers(project_root)

            if not dead:
                return ReconcileResult(
                    action="clean",
                    detail="no dead public wrappers found",
                    gate_id=_GATE_ID,
                )

            # 格式化 detail（截断防过长）
            items = [f"{d['file']}:{d['function']} (line {d['line']}, {d['scope']})" for d in dead[:_MAX_DETAIL_ITEMS]]
            detail = f"{len(dead)} dead public wrapper(s): {'; '.join(items)}"
            if len(dead) > _MAX_DETAIL_ITEMS:
                detail += f"; ... and {len(dead) - _MAX_DETAIL_ITEMS} more"

            return ReconcileResult(
                action="warn",
                detail=detail,
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("dead_public_wrapper: reconcile failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"dead_public_wrapper reconcile error: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
