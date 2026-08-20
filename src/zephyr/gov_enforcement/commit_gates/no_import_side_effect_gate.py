# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.no_import_side_effect_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file, _get_added_lines); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged src/ .py 文件 added 行中模块级副作用调用阻断 commit（passed=False）；只检测 added 行（防误阻断现有 2288 文件存量违规，对标 TEST-SOURCE-CONSISTENCY 只防新增策略）；tests/ 豁免（is_test_exempt）；__main__.py 豁免（入口点，module-level 代码预期在 python -m 时执行）；if __name__ == "__main__" guard 块豁免（仅脚本直接执行时运行，import 时不触发）；FunctionDef/ClassDef 体豁免（非模块级）；检测两类：(1) I/O/网络/subprocess/DB 调用 open/urlopen/subprocess.*/requests.*/socket.socket/duckdb.connect 等 + Path(...).read_text/write_text/... 方法调用；(2) 急切单例实例化 UPPER_SNAKE 目标 = Capitalized 调用（如 TELEMETRY = InventorySelfMetrics()），allowlist 纯构造 TypeVar/NamedTuple/TypedDict/Enum/Path；AST/git 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="NO-IMPORT-SIDE-EFFECT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；_SIDE_EFFECT_FUNCS / _PATH_IO_METHODS / _PURE_CAPITALIZED 集合
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_no_import_side_effect_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: in-process 门禁检测器（GitCommitGateway 事件触发，STARTUP=imported），检测模式字符串非真实 manual 触发
"""no_import_side_effect_gate.py — 模块导入零副作用门禁（NO-IMPORT-SIDE-EFFECT，S4-C 2026-07-17）

检测 staged src/ .py 文件 added 行中的模块级副作用——违反"模块导入零副作用原则"
（import 一个模块不应触发 I/O、网络、子进程、DB 连接或急切实例化）。

病根（第一性原理）
-----------------
S4-A 审计发现两类模块导入副作用违规：
  1. ``telemetry.py`` 模块级 ``TELEMETRY = InventorySelfMetrics()`` 急切实例化——
     import telemetry 即创建单例，违反零副作用原则。
  2. ``rollback/__init__.py`` 急切 ``from . import (37 子模块)``——import rollback
     即触发 37 个子模块的模块级代码执行（含 3 个 deprecated 子模块）。

S4-A 已修复（TELEMETRY 改惰性 + 移除 3 个废弃子模块急切导入）。本 gate 防止
新 AI 制造同类债务——commit 阶段硬阻断新增模块级副作用。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified src/ .py 文件（tests/ + __main__.py 豁免）
  2. 获取每文件 added 行号集合（只检测新增副作用，不误阻断存量）
  3. AST 解析，遍历模块级语句（descend through If/Try/With/For/While，
     跳过 FunctionDef/ClassDef 体 + if __name__ == "__main__" guard 块）
  4. 检测两类违规：
     a. I/O/网络/subprocess/DB 调用（open/urlopen/subprocess.*/requests.*/
        socket.socket/duckdb.connect/psycopg2.connect/sqlite3.connect +
        Path(...).read_text/write_text/... 方法调用）
     b. 急切单例实例化（UPPER_SNAKE 目标 = Capitalized 调用，
        如 TELEMETRY = InventorySelfMetrics()；allowlist 纯构造
        TypeVar/NamedTuple/TypedDict/Enum/Path）
  5. 违规 Call 的 lineno 在 added_lines 中 -> 硬阻断

设计权衡
--------
1. **只检测 added 行**：存量 2288 文件有大量模块级副作用（如 ``logger = logging.getLogger()``
   无害、历史 eager singleton 等），全量检测会误阻断。对标 TEST-SOURCE-CONSISTENCY
   "只防新增"策略，grandfather 存量。
2. **tests/ 豁免**：测试文件 module-level fixture/setup 是合理副作用。
3. **__main__.py 豁免**：入口点 module-level 代码预期在 ``python -m`` 时执行。
4. **if __name__ guard 豁免**：``if __name__ == "__main__":`` 块仅脚本直接执行时运行，
   import 时不触发，不算导入副作用。
5. **急切单例启发式**：UPPER_SNAKE 目标 + Capitalized 调用——高精度低误报：
   - 命中 ``TELEMETRY = InventorySelfMetrics()``、``CLIENT = HttpClient()``
   - 不命中 ``logger = logging.getLogger()``（目标小写）、``RE = re.compile()``（func 小写）
   - 不命中 ``DEFAULT = defaultdict(list)``（func 小写）、``PATH = Path("/x")``（allowlist）
6. **fail-open on AST/git error**：语法错误文件不阻断（由其他 gate 管语法）。
7. **priority=103**：在 TEST-SOURCE-CONSISTENCY(102) 之后，作为 commit 流程末段 gate。

Usage::

    from zephyr.gov_enforcement.commit_gates.no_import_side_effect_gate import make_no_import_side_effect_gate

    registry.register(make_no_import_side_effect_gate())
"""

from __future__ import annotations

import ast
import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_no_import_side_effect_gate"]

# I/O/网络/subprocess/DB 副作用调用——(module_attr, {funcs}) 或裸函数名
# 裸函数名（Name 调用）：
_SIDE_EFFECT_BUILTINS: set[str] = {"open", "urlopen"}
# Attribute 调用：module.func 形式（module 是 ast.Name.id）
_SIDE_EFFECT_ATTRS: dict[str, set[str]] = {
    "subprocess": {"run", "call", "Popen", "check_output", "check_call"},
    "requests": {"get", "post", "put", "delete", "patch", "head", "request"},
    "socket": {"socket"},
    "duckdb": {"connect"},
    "psycopg2": {"connect"},
    "sqlite3": {"connect"},
    "mysql": {"connector"},  # mysql.connector.connect — 保守标记
}
# Path(...).<io_method> 方法调用——检测 Attribute(value=Call(func=Path)).<method>
_PATH_IO_METHODS: set[str] = {
    "read_text",
    "read_bytes",
    "write_text",
    "write_bytes",
    "read",
    "write",
    "unlink",
    "mkdir",
    "rmdir",
    "touch",
}
# 急切单例 allowlist——Capitalized 但纯构造（无 I/O/无副作用）
_PURE_CAPITALIZED: set[str] = {"TypeVar", "NamedTuple", "TypedDict", "Enum", "Path"}
# UPPER_SNAKE 目标判定：至少 2 个大写字符（避免单字母 A/B 误判）
_UPPER_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")


def _is_name_main_guard(test: ast.expr) -> bool:
    """检测 ``if __name__ == "__main__":`` 守卫（import 时不触发的块）。"""
    if not isinstance(test, ast.Compare):
        return False
    if not (isinstance(test.left, ast.Name) and test.left.id == "__name__"):
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    cmp = test.comparators[0]
    return isinstance(cmp, ast.Constant) and isinstance(cmp.value, str) and cmp.value == "__main__"


def _call_func_name(call: ast.Call) -> str:
    """提取 Call 的函数名（用于错误消息）——Name.id 或 Attribute.attr 或 unparse。"""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    try:
        return ast.unparse(func)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return "<call>"


def _is_side_effect_call(call: ast.Call) -> tuple[bool, str]:
    """判定 Call 是否为 I/O/网络/subprocess/DB 副作用调用。

    Returns:
        (True, description) 命中副作用； (False, "") 未命中。
    """
    func = call.func
    # 裸函数名：open(...) / urlopen(...)
    if isinstance(func, ast.Name) and func.id in _SIDE_EFFECT_BUILTINS:
        return True, f"{func.id}(...) 模块级 I/O 调用"
    # module.func 形式：subprocess.run / requests.get / duckdb.connect / ...
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            mod = func.value.id
            if mod in _SIDE_EFFECT_ATTRS and func.attr in _SIDE_EFFECT_ATTRS[mod]:
                return True, f"{mod}.{func.attr}(...) 模块级副作用调用"
        # Path(...).read_text/write_text/... 方法调用
        if func.attr in _PATH_IO_METHODS and isinstance(func.value, ast.Call):
            inner = func.value.func
            if (isinstance(inner, ast.Name) and inner.id == "Path") or (
                isinstance(inner, ast.Attribute) and inner.attr == "Path"
            ):
                return True, f"Path(...).{func.attr}(...) 模块级 Path I/O 调用"
    return False, ""


def _is_eager_singleton(assign: ast.Assign) -> tuple[bool, str]:
    """判定 Assign 是否为急切单例实例化（UPPER_SNAKE 目标 = Capitalized 调用）。

    Returns:
        (True, description) 命中急切单例； (False, "") 未命中。
    """
    if len(assign.targets) != 1:
        return False, ""
    target = assign.targets[0]
    if not (isinstance(target, ast.Name) and _UPPER_NAME_RE.match(target.id)):
        return False, ""
    value = assign.value
    if not isinstance(value, ast.Call):
        return False, ""
    func = value.func
    cap_name: str | None = None
    if isinstance(func, ast.Name):
        cap_name = func.id
    elif isinstance(func, ast.Attribute):
        cap_name = func.attr
    if cap_name is None or not cap_name[:1].isupper():
        return False, ""
    if cap_name in _PURE_CAPITALIZED:
        return False, ""
    return True, f"{target.id} = {cap_name}(...) 模块级急切单例实例化"


def _iter_module_level_exprs(body: list[ast.stmt]):
    """递归遍历模块级语句，yield (node, value_expr) 对供副作用检测。

    降级进入 If（非 __name__ guard）/Try/With/For/While 体；跳过
    FunctionDef/AsyncFunctionDef/ClassDef 体（非模块级）。
    yield 的 node 是承载副作用的语句（Assign/AnnAssign/Expr/With-item）。
    """
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.If):
            if _is_name_main_guard(node.test):
                continue
            yield from _iter_module_level_exprs(node.body)
            yield from _iter_module_level_exprs(node.orelse)
            continue
        if isinstance(node, ast.Try):
            yield from _iter_module_level_exprs(node.body)
            for handler in node.handlers:
                yield from _iter_module_level_exprs(handler.body)
            yield from _iter_module_level_exprs(node.orelse)
            yield from _iter_module_level_exprs(node.finalbody)
            continue
        if isinstance(node, (ast.With, ast.AsyncWith)):
            # with 项的 context_expr 可能含副作用（with open(...):）
            for item in node.items:
                yield (item, item.context_expr)
            yield from _iter_module_level_exprs(node.body)
            continue
        if isinstance(node, (ast.For, ast.While)):
            yield from _iter_module_level_exprs(node.body)
            yield from _iter_module_level_exprs(node.orelse)
            continue
        if isinstance(node, ast.Assign):
            yield (node, node.value)
        elif isinstance(node, ast.AnnAssign):
            if node.value is not None:
                yield (node, node.value)
        elif isinstance(node, ast.Expr):
            yield (node, node.value)


def _check_file(content: str, py_file: str, added_lines: set[int]) -> list[str]:
    """检查单个文件的模块级副作用（仅 added 行），返回违规描述列表。"""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []  # 语法错误由其他 gate 处理
    violations: list[str] = []
    for node, value in _iter_module_level_exprs(tree.body):
        # 急切单例检查（仅 Assign）
        if isinstance(node, ast.Assign):
            is_sin, desc = _is_eager_singleton(node)
            if is_sin and node.lineno in added_lines:
                violations.append(f"  {py_file}:{node.lineno}: {desc}")
        # I/O 副作用检查——遍历 value 中所有 Call 节点
        for call in ast.walk(value):
            if not isinstance(call, ast.Call):
                continue
            if call.lineno not in added_lines:
                continue
            is_io, desc = _is_side_effect_call(call)
            if is_io:
                violations.append(f"  {py_file}:{call.lineno}: {desc}")
    return violations


def _is_main_entry(py_file: str) -> bool:
    """__main__.py 入口点豁免（module-level 代码预期在 python -m 时执行）。"""
    return py_file.replace("\\", "/").endswith("/__main__.py")


def make_no_import_side_effect_gate() -> GateSpec:
    """构造模块导入零副作用门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-IMPORT-SIDE-EFFECT", priority=103)。
        priority=103——在 TEST-SOURCE-CONSISTENCY(102) 之后，commit 流程末段。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        staged = _get_staged_py_files(gateway, gate_name="NO-IMPORT-SIDE-EFFECT")
        if not staged:
            return True, ""

        # 2. 过滤 tests/ + __main__.py 豁免
        src_files = [f for f in staged if not is_test_exempt(f) and not _is_main_entry(f)]
        if not src_files:
            return True, ""

        # 3. 逐文件检测（仅 added 行）
        all_violations: list[str] = []
        for py_file in src_files:
            content = _read_staged_file(gateway, py_file)
            if not content:
                continue
            added = _get_added_lines(gateway, py_file, gate_name="NO-IMPORT-SIDE-EFFECT")
            added_lines = {ln for ln, _ in added} if added else set()
            if not added_lines:
                continue  # 无新增行，跳过（纯删除/修改注释等）
            all_violations.extend(_check_file(content, py_file, added_lines))

        # 4. 硬阻断
        if all_violations:
            detail = (
                "NO-IMPORT-SIDE-EFFECT (S4-C 模块导入零副作用原则)：检测到模块级副作用\n"
                "  import 一个模块不应触发 I/O、网络、子进程、DB 连接或急切实例化。\n"
                + "\n".join(all_violations)
                + "\n-> 改为惰性：将副作用移入函数（首次调用时执行）或 __getattr__ (PEP 562)"
                + '\n   或 if __name__ == "__main__" guard；急切单例改 get_xxx() 惰性工厂'
            )
            logger.error("NO-IMPORT-SIDE-EFFECT gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="NO-IMPORT-SIDE-EFFECT", check=_check, priority=103)
