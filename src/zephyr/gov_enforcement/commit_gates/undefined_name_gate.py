# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.undefined_name_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.governance.audit.reconciliation_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-open（ast 语法错误/git 失败/文件不可读时放行，语法类问题由其他阶段检测）；wildcard import 跳过（导入集无法静态推断，权衡漏报优先零误报）；纯 stdlib AST 无第三方依赖
# [MODIFY-GUARD] gate_id=UNDEFINED-NAME；priority=106；扫描范围 scripts/governance/** + src/**.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 返回 (False, detail) 阻断 | (True, "") 放行
# [TESTS] tests/governance/commit_gates/test_undefined_name_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定义符号硬阻断）

GATE-DEPGRAPH-OPS 治本 Phase 1（F821 零防护缺口）：
AI 提交路径（GitCommitGateway / session_worktree）以 --no-verify 绕过外部
pre-commit hook，ruff/flake8 的 F821（undefined name）检测完全不执行——
AI 生成的代码引用未定义符号（笔误/幻觉 API/误删 import）时零防护，
NameError 直到运行时才暴露（deb695006f 误删 import 事故同型缺口）。

治本：in-process stdlib AST 检测 staged scripts/governance/** 与 src/**.py
中的未定义符号，commit 阶段硬阻断。覆盖 import / 本地定义（函数/类/赋值/
参数/for/with/except/lambda/comprehension/global/nonlocal/match 捕获）/
builtins / dunder 全场景。与 ruff F821 全扫比对 0 误报（2026-07-19，
.runtime/_f821_compare.py）；5 个已知漏报全部源于 wildcard import 跳过
策略——权衡后接受（wildcard 导入集无法静态推断，误报会阻断合法代码）。

post-commit 补强：make_undefined_name_baseline_reconciler（reconciliation_registry，
GATE-UNDEFINED-NAME-BASELINE, priority=211）全仓 baseline 扫描，覆盖 gate
上线前存量债务与 --no-verify 绕过盲区。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: py_file 参数
#   fields: 参数 py_file，类型注解 str
#   code: undefined_name_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: undefined_name_gate.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: undefined_name_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① scan_content_for_undefined_names
#   name_en: scan_content_for_undefined_names
#   intro: 扫描单文件内容的未定义符号（F821），返回违规消息列表（空=通过）。
#   desc: 扫描单文件内容的未定义符号（F821），返回违规消息列表（空=通过）。 fail-open：语法错误返回空（语法问题由其他阶段检测，不在本 gate 职责）。 wildcard…；源码 L297-L319
#   inputs: py_file content
#   outputs: list[str]
# - id: A2
#   name_zh: ② scan_all_for_undefined_names
#   name_en: scan_all_for_undefined_names
#   intro: 全仓 baseline 扫描 scripts/governance/** + src/**.py 的未定义符号。
#   desc: 全仓 baseline 扫描 scripts/governance/** + src/**.py 的未定义符号。 与 make_undefined_name_gate（pre-c…；源码 L322-L362
#   inputs: project_root
#   outputs: tuple[list[str], str | None]
# - id: A3
#   name_zh: ③ make_undefined_name_gate
#   name_en: make_undefined_name_gate
#   intro: 构造 UNDEFINED-NAME pre-commit 门禁（priority=106）。
#   desc: 构造 UNDEFINED-NAME pre-commit 门禁（priority=106）。 检测 staged scripts/governance/** + src/**.p…；源码 L365-L408
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.governance.audit.…
# - id: O2
#   name_zh: tuple[list[str], str | None]
#   name_en: tuple[list[str], str | None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.governance.audit.…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import ast
import builtins
import glob
import logging
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = [
    "make_undefined_name_gate",
    "scan_all_for_undefined_names",
    "scan_content_for_undefined_names",
]

# 扫描范围：与 SCRIPTS-IMPORT-INTEGRITY 对齐 + src/（AI 生成代码主战场）
_SCAN_PREFIXES: tuple[str, ...] = ("scripts/governance/", "src/")

# 隐式可用名：builtins 全集 + 模块级 dunder（__name__/__file__ 等）
_IMPLICIT_NAMES: frozenset[str] = frozenset(
    set(dir(builtins))
    | {
        "__name__",
        "__file__",
        "__doc__",
        "__all__",
        "__package__",
        "__path__",
        "__spec__",
        "__loader__",
        "__cached__",
        "__builtins__",
        "__annotations__",
        "__qualname__",
        "__module__",
        "__dict__",
        "__class__",
        "__slots__",
        "__version__",
        "__manifest__",
    }
)


def _collect_imported_names(tree: ast.AST) -> tuple[set[str], bool]:
    """收集 import 引入的名字；返回 (名字集, 是否含 wildcard import)。"""
    imported: set[str] = set()
    has_wildcard = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # import a.b.c -> 绑定 a；import a.b as x -> 绑定 x
                imported.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    has_wildcard = True
                else:
                    imported.add(alias.asname or alias.name)
    return imported, has_wildcard


def _collect_match_capture_names(pattern: ast.AST) -> set[str]:
    """收集 match case 模式的捕获名（MatchAs/MatchStar/MatchMapping rest 等）。"""
    names: set[str] = set()
    for node in ast.walk(pattern):
        if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            names.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            names.add(node.rest)
    return names


def _collect_target_names(target: ast.AST) -> set[str]:
    """收集赋值/for/with/except 目标的绑定名（Name/Tuple/List/Starred 递归）。"""
    names: set[str] = set()
    for node in ast.walk(target):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Param)):
            names.add(node.id)
    return names


def _collect_module_name_sets(body: list) -> dict[str, set[str]]:
    """收集模块级 *_NAMES 集合字面量（惰性导出符号登记表）。"""
    name_sets: dict[str, set[str]] = {}
    for stmt in body:
        if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1):
            continue
        target = stmt.targets[0]
        if not (
            isinstance(target, ast.Name)
            and target.id.endswith("_NAMES")
            and isinstance(stmt.value, (ast.Set, ast.List, ast.Tuple))
        ):
            continue
        name_sets[target.id] = {
            elt.value for elt in stmt.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        }
    return name_sets


def _extract_getattr_lazy_names(stmt: ast.AST, name_sets: dict[str, set[str]]) -> set[str]:
    """从单个 __getattr__ 函数体提取惰性导出符号（name == "X" / name in _XXX_NAMES）。"""
    lazy: set[str] = set()
    args = getattr(stmt, "args", None)
    param = args.args[0].arg if args and args.args else "name"
    for node in ast.walk(stmt):
        if not isinstance(node, ast.Compare):
            continue
        if not (isinstance(node.left, ast.Name) and node.left.id == param):
            continue
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if isinstance(op, ast.Eq) and isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                lazy.add(comparator.value)
            elif isinstance(op, ast.In) and isinstance(comparator, ast.Name):
                lazy.update(name_sets.get(comparator.id, set()))
    return lazy


def _collect_lazy_getattr_names(tree: ast.AST) -> set[str]:
    """收集 PEP 562 模块级 __getattr__ 惰性导出的符号名。

    背景（2026-07-19 存量债务治理发现）：项目刻意使用 module __getattr__ +
    importlib 惰性导入规避分层违规边（如 L0 shared -> L3 trading 的 CurrencyCode、
    shared -> gov_enforcement 的 TaskStatus、跨域重型依赖 InputSanitizer）。
    运行时由 __getattr__ 解析，静态扫描需识别该模式，避免对刻意架构误报。
    """
    body = getattr(tree, "body", [])
    name_sets = _collect_module_name_sets(body)
    lazy: set[str] = set()
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == "__getattr__":
            lazy.update(_extract_getattr_lazy_names(stmt, name_sets))
    return lazy


def _collect_defined_names(tree: ast.AST) -> set[str]:
    """收集模块内所有本地定义名（声明即定义——Python 无块级作用域，顺序不敏感）。

    覆盖：def/async def/class/赋值目标/参数/for 目标/with as/except as/
    lambda 参数/推导式变量/global & nonlocal 声明/match 捕获。
    """
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args
                defined.update(a.arg for a in args.posonlyargs + args.args + args.kwonlyargs)
                if args.vararg:
                    defined.add(args.vararg.arg)
                if args.kwarg:
                    defined.add(args.kwarg.arg)
        elif isinstance(node, ast.Lambda):
            args = node.args
            defined.update(a.arg for a in args.posonlyargs + args.args + args.kwonlyargs)
            if args.vararg:
                defined.add(args.vararg.arg)
            if args.kwarg:
                defined.add(args.kwarg.arg)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                defined.update(_collect_target_names(t))
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            defined.update(_collect_target_names(node.target))
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    defined.update(_collect_target_names(item.optional_vars))
        elif isinstance(node, ast.ExceptHandler) and node.name:
            defined.add(node.name)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for comp in node.generators:
                defined.update(_collect_target_names(comp.target))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            defined.update(node.names)
        elif isinstance(node, ast.match_case):
            defined.update(_collect_match_capture_names(node.pattern))
        elif isinstance(node, ast.NamedExpr):
            defined.update(_collect_target_names(node.target))
    defined.update(_collect_lazy_getattr_names(tree))
    return defined


def _find_first_use_line(tree: ast.AST, symbol: str) -> int:
    """找符号首次 Load 使用的行号（诊断定位用）。"""
    first = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == symbol and isinstance(node.ctx, ast.Load):
            if first == 0 or node.lineno < first:
                first = node.lineno
    return first


def scan_content_for_undefined_names(py_file: str, content: str) -> list[str]:
    """扫描单文件内容的未定义符号（F821），返回违规消息列表（空=通过）。

    fail-open：语法错误返回空（语法问题由其他阶段检测，不在本 gate 职责）。
    wildcard import 跳过（导入集无法静态推断——宁漏报不误报）。
    """
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        return []  # fail-open：语法错误由其他阶段检测

    imported, has_wildcard = _collect_imported_names(tree)
    if has_wildcard:
        return []  # 跳过：wildcard 导入集无法静态推断

    defined = _collect_defined_names(tree)
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    missing = used - imported - defined - _IMPLICIT_NAMES
    violations: list[str] = []
    for sym in sorted(missing):
        line_no = _find_first_use_line(tree, sym)
        violations.append(f"  {py_file}:{line_no}: undefined name '{sym}' (not imported, not defined locally)")
    return violations


def scan_all_for_undefined_names(
    project_root: Path,
) -> tuple[list[str], str | None]:
    """全仓 baseline 扫描 scripts/governance/** + src/**.py 的未定义符号。

    与 make_undefined_name_gate（pre-commit）的区别：gate 扫 staged 硬阻断；
    本函数扫全仓磁盘文件，供 post-commit reconciler baseline 全扫（warn 级）。
    与 gate 共享 scan_content_for_undefined_names（DRY，零新真源）。

    Returns:
        (violations, error_msg)：error_msg 非 None 表示 fail-open（目录不存在），
        调用方应降级为 ReconcileResult(action="skip")。
    """
    root = Path(str(project_root))
    gov_dir = root / "scripts" / "governance"
    src_dir = root / "src"
    if not gov_dir.exists() and not src_dir.exists():
        return [], "scripts/governance/ 与 src/ 均不存在"

    violations: list[str] = []
    for base, prefix in ((gov_dir, "scripts/governance/"), (src_dir, "src/")):
        if not base.exists():
            continue
        for py_file_path in glob.glob(str(base / "**" / "*.py"), recursive=True):
            # 裁定#E（2026-07-19）：排除 _archive 目录（归档代码不参与 F821 扫描）
            # 病根：归档目录中的死代码触发 F821 误报，干扰存量债务治理
            if "_archive" in py_file_path:
                continue
            rel = py_file_path.replace("\\", "/")
            idx = rel.find(prefix)
            if idx < 0:
                continue
            py_file = rel[idx:]
            try:
                with open(py_file_path, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue  # fail-open: 文件不可读
            violations.extend(scan_content_for_undefined_names(py_file, content))

    return violations, None


def make_undefined_name_gate() -> GateSpec:
    """构造 UNDEFINED-NAME pre-commit 门禁（priority=106）。

    检测 staged scripts/governance/** + src/**.py 的未定义符号（F821），
    硬阻断。fail-open：无 staged 文件/git 失败/文件不可读时放行。
    """

    def _check(gateway, _files: list[str], **_kwargs) -> tuple[bool, str]:
        staged = _get_staged_py_files(gateway, "UNDEFINED-NAME")
        if not staged:
            return True, ""

        violations: list[str] = []
        for py_file in staged:
            if not py_file.startswith(_SCAN_PREFIXES):
                continue
            # 裁定#E（2026-07-19）同口径补齐：staged 路径与 scan_all_for_undefined_names
            # 一致排除 _archive（归档一次性死代码不参与 F821 扫描；2026-08-20 波3 实证
            # format 重排归档脚本存量符号伪"新增"致误阻断 migrate_clean_build_status.py）
            if "_archive" in py_file:
                continue
            content = _read_staged_file(gateway, py_file)
            if content is None:
                continue  # fail-open: 文件不可读（git show 失败）
            violations.extend(scan_content_for_undefined_names(py_file, content))

        if violations:
            detail = (
                "UNDEFINED-NAME: 使用了未定义的符号（F821，GATE-DEPGRAPH-OPS 治本 Phase 1）\n"
                "  病根：符号未 import 也未本地定义，运行时才抛 NameError——\n"
                "  AI 提交路径 --no-verify 绕过外部 pre-commit，ruff F821 零防护。\n"
                "  修复：补 import / 修正拼写 / 补本地定义后重新 commit。\n"
                + "\n".join(violations[:50])
                + (f"\n  ...(+{len(violations) - 50} more)" if len(violations) > 50 else "")
            )
            logger.error("UNDEFINED-NAME gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(
        gate_id="UNDEFINED-NAME",
        check=_check,
        priority=106,
    )
