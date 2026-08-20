# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.scripts_import_integrity_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance._shared.constants
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ ; zephyr.governance.audit.reconciliation_registry.make_scripts_import_integrity_reconciler (Phase 3 baseline 全扫)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged scripts/governance/**/*.py 文件中 _shared.constants 公开符号被使用但未 import 时阻断（#ARCH-DATAQUALITY-V1.4 核心治本）；豁免 _shared/constants.py（真源文件，不可自引用）；含 wildcard import 的文件跳过（无法静态推断）；_shared.constants 不可导入时 fail-open；ast.parse 失败 fail-open（语法错误文件本就会在其他阶段失败）
# [MODIFY-GUARD] gate_id="SCRIPTS-IMPORT-INTEGRITY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——_shared.constants 导入失败/ast.parse 失败/文件不可读降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_scripts_import_integrity_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scripts_import_integrity_gate.py — _shared.constants 符号导入完整性门禁

检测 staged scripts/governance/**/*.py 文件中 _shared.constants 公开符号被使用
但未 import 的违规（#ARCH-DATAQUALITY-V1.4 核心治本）。

病根（第一性原理）
-----------------
裁定 #ARCH-DATAQUALITY-V1 审查发现 4 个 governance 脚本使用 _shared.constants 的
REPO_ROOT / get_depgraph_pg_connection 等符号但未 import，导致运行时 NameError：

  - analyze_change_impact.py（缺 REPO_ROOT + get_depgraph_pg_connection）
  - audit_rename_completeness.py（缺 REPO_ROOT + get_depgraph_pg_connection）
  - validate_target_layer.py（缺 REPO_ROOT）
  - governance_watchdog.py（缺 _shared bootstrap + REPO_ROOT）

根因：无 commit 阶段强制——AI 复制现有模式时遗漏 import，静默累积债务。
Task A 已修复这 4 个文件，本 gate 是治本——防止未来 AI 重蹈覆辙。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁：
  1. 动态获取 _shared.constants 公开符号集合（dir() 过滤私有名 _ 开头）
  2. 对每个 staged scripts/governance/**/*.py 文件做 ast 解析
  3. 收集 imported_names（ImportFrom/Import 节点）+ defined_names（Store ctx Name
     + arg + FunctionDef/ClassDef name + Global/Nonlocal + ExceptHandler.name）
  4. 收集 used_names（Load ctx Name 节点）
  5. 对每个 _shared.constants 符号：used 且 not imported 且 not defined → 违规
  6. 硬阻断

设计权衡
--------
1. **只检测 scripts/governance/**：src/ 有 validate_python_syntax.py 覆盖，
   tests/ 不依赖 _shared.constants。聚焦 governance 脚本域。
2. **ast-based**：与 blueprint_format_gate / bare_sql_gate 一致的检测模式。
3. **动态符号集**：通过 dir(_shared.constants) 获取真实导出集（30 个公开符号），
   而非硬编码符号列表——硬编码会随 _shared.constants 演进而过时。
4. **含 wildcard import 的文件跳过**：`from X import *` 无法静态推断导入了哪些
   符号，跳过避免假阳性（false positive）。
5. **_shared/constants.py 豁免**：真源文件不可自引用 import，豁免避免循环检测。
6. **priority=104**：在 NO-IMPORT-SIDE-EFFECT(103) 之后，属 import-related gate 组
   （IMPORT-DIRECTION=97, TEST-SOURCE-CONSISTENCY=102, NO-IMPORT-SIDE-EFFECT=103）。
7. **fail-open on _shared.constants import failure**：_shared.constants 依赖
   psycopg2 和 zephyr 模块，若环境不可用则 fail-open（不阻断 commit），记录 warning。
8. **defined_names 全覆盖**：收集 Store-ctx Name / arg / FunctionDef / ClassDef /
   Global / Nonlocal / ExceptHandler.name，避免将局部变量误报为缺失 import。

Usage::

    from zephyr.gov_enforcement.commit_gates.scripts_import_integrity_gate import (
        make_scripts_import_integrity_gate,
    )
    registry.register(make_scripts_import_integrity_gate())
"""

from __future__ import annotations

import ast
import glob
import logging
import sys
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# 治本 #ARCH-TOOL-HEALTH-V1 Phase 3：scan_all_scripts_for_import_violations 供
# post-commit reconciler（make_scripts_import_integrity_reconciler）做 baseline 全扫，
# 补强 pre-commit gate 只扫 staged 文件的盲区（gate 上线前的基线 bug 永远扫不到）。
__all__ = [
    "make_scripts_import_integrity_gate",
    "scan_all_scripts_for_import_violations",
]

# 豁免：_shared/constants.py 是 _shared.constants 真源，不可自引用 import
_EXEMPT_FILES: frozenset[str] = frozenset({"scripts/governance/_shared/constants.py"})


def _get_shared_constants_symbols() -> set[str] | None:
    """动态获取 _shared.constants 公开符号集合。

    通过 dir(_shared.constants) 获取所有属性，过滤私有名（_ 开头）。
    包含 _shared.constants 自身定义的符号（REPO_ROOT re-export、EXIT_PASS 等）
    和它导入的符号（Path、Any、sys 等——脚本若使用这些符号也必须显式 import）。

    Returns:
        符号集合，或 None（_shared.constants 不可导入时，调用方应 fail-open）。
    """
    try:
        _gov_dir = str(REPO_ROOT / "scripts" / "governance")
        if _gov_dir not in sys.path:
            sys.path.insert(0, _gov_dir)
        import _shared.constants as _sc  # noqa: PLC0415 — lazy import for fail-open

        return {name for name in dir(_sc) if not name.startswith("_")}
    except Exception as e:  # noqa: BLE001 — fail-open on import error
        logger.warning(
            "SCRIPTS-IMPORT-INTEGRITY: _shared.constants 不可导入，fail-open: %s: %s",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _collect_imported_names(tree: ast.AST) -> tuple[set[str], bool]:
    """收集文件中所有显式 import 的符号名。

    Returns:
        (imported_names, has_wildcard) —— has_wildcard=True 表示文件含
        ``from X import *``，调用方应跳过该文件（无法静态推断 wildcard 导入集）。
    """
    imported: set[str] = set()
    has_wildcard = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    has_wildcard = True
                    continue
                imported.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    imported.add(alias.asname)
                else:
                    # import foo.bar → 只有 foo 可访问（foo.bar 经属性访问）
                    imported.add(alias.name.split(".")[0])
    return imported, has_wildcard


def _collect_defined_names(tree: ast.AST) -> set[str]:
    """收集文件中所有本地定义的符号名。

    覆盖：
    - Store-ctx Name（赋值/循环变量/with as/增强赋值/comprehension 目标）
    - arg（函数参数/lambda 参数）
    - FunctionDef / AsyncFunctionDef / ClassDef 的 name
    - Global / Nonlocal 声明的 names
    - ExceptHandler.name（except E as e 的 e）
    """
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            defined.update(node.names)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                defined.add(node.name)
    return defined


def _collect_used_names(tree: ast.AST) -> set[str]:
    """收集文件中所有被使用的符号名（Load context 的 Name 节点）。"""
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}


def _find_first_use_line(tree: ast.AST, symbol: str) -> int:
    """找到符号在文件中首次使用的行号（Load context）。

    ast.walk 不保证顺序，收集所有命中行号后取最小值。
    """
    candidates = [
        node.lineno
        for node in ast.walk(tree)
        if (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id == symbol)
    ]
    return min(candidates) if candidates else 0


def _scan_file_content(py_file: str, content: str, shared_symbols: set[str]) -> list[str]:
    """扫描单个文件内容，返回 _shared.constants 符号使用未导入的违规列表。

    治本 #ARCH-TOOL-HEALTH-V1 Phase 3：提取为共享 helper，供 pre-commit gate
    （staged 文件扫描）和 post-commit reconciler（全仓 baseline 扫描）复用，
    消除检测逻辑重复（DRY）。

    Args:
        py_file: 文件路径（用于违规消息显示，相对路径格式 scripts/governance/...）。
        content: 文件文本内容。
        shared_symbols: _shared.constants 公开符号集合。

    Returns:
        该文件的违规消息列表（每条形如 "  path:line: symbol 'X' used but not
        imported..."）。空列表表示无违规、语法错误、或含 wildcard import（跳过）。
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # fail-open: 语法错误文件本就会在其他阶段失败
        return []

    imported, has_wildcard = _collect_imported_names(tree)
    if has_wildcard:
        # 跳过：wildcard import 无法静态推断导入集
        return []

    defined = _collect_defined_names(tree)
    used = _collect_used_names(tree)

    # 检测：_shared.constants 符号 used 但 not imported 且 not defined
    missing = shared_symbols & used - imported - defined
    violations: list[str] = []
    if missing:
        for sym in sorted(missing):
            line_no = _find_first_use_line(tree, sym)
            violations.append(
                f"  {py_file}:{line_no}: symbol '{sym}' used but not "
                f"imported from _shared.constants (nor defined locally)"
            )
    return violations


def make_scripts_import_integrity_gate() -> GateSpec:
    """构造 _shared.constants 符号导入完整性门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="SCRIPTS-IMPORT-INTEGRITY", priority=104)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        shared_symbols = _get_shared_constants_symbols()
        if shared_symbols is None:
            # fail-open: _shared.constants 不可导入（环境问题，不阻断 commit）
            return True, ""

        py_files = _get_staged_py_files(gateway, "SCRIPTS-IMPORT-INTEGRITY")
        # 只检测 scripts/governance/**/*.py（src/ 由 validate_python_syntax 覆盖，
        # tests/ 不依赖 _shared.constants）
        gov_scripts = [f for f in py_files if f.replace("\\", "/").startswith("scripts/governance/")]

        violations: list[str] = []
        for py_file in gov_scripts:
            normalized = py_file.replace("\\", "/")
            if normalized in _EXEMPT_FILES:
                continue
            content = _read_staged_file(gateway, py_file)
            if content is None:
                # fail-open: 文件不可读（git show 失败）
                continue
            # 治本 #ARCH-TOOL-HEALTH-V1 Phase 3：复用 _scan_file_content helper
            # （与 post-commit reconciler baseline 全扫共享同一检测逻辑，DRY）
            violations.extend(_scan_file_content(py_file, content, shared_symbols))

        if violations:
            detail = (
                "SCRIPTS-IMPORT-INTEGRITY: _shared.constants 符号被使用但未 import"
                "（#ARCH-DATAQUALITY-V1.4 核心治本）\n"
                "  病根：脚本使用 _shared.constants 的 REPO_ROOT / "
                "get_depgraph_pg_connection 等符号但未 import，导致运行时 NameError。\n"
                "  修复：在文件顶部添加 "
                "`from _shared.constants import <symbol>`\n" + "\n".join(violations)
            )
            logger.error("SCRIPTS-IMPORT-INTEGRITY gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(
        gate_id="SCRIPTS-IMPORT-INTEGRITY",
        check=_check,
        priority=104,
    )


# 治本 #ARCH-TOOL-HEALTH-V1 Phase 3：baseline 全扫公开入口。
# 病根：pre-commit gate 只扫 staged 文件（incremental-only），gate 上线前的基线
# bug（如 deb695006f 误删 import）永远不会被扫到。本函数扫描磁盘上所有
# scripts/governance/**/*.py 文件，供 post-commit reconciler 定期跑全仓补强。
def scan_all_scripts_for_import_violations(
    project_root: Path,
) -> tuple[list[str], str | None]:
    """全仓 baseline 扫描 scripts/governance/**/*.py 的 _shared.constants 导入完整性。

    与 make_scripts_import_integrity_gate（pre-commit gate）的区别：
    - **gate（pre-commit）**：扫 staged 文件，硬阻断（passed=False 阻断 commit）。
    - **本函数（post-commit reconciler baseline）**：扫全仓磁盘文件，warn 级
      （commit 已入库不可阻断；violations 报告为 warn 供 AI 修复）。

    复用 _scan_file_content helper，与 gate 共享同一检测逻辑（DRY）。

    Args:
        project_root: 仓库根 Path 对象（zephyr.shared.io.paths.REPO_ROOT）。

    Returns:
        (violations, error_msg):
        - violations: 违规消息列表（空列表=无违规）。
        - error_msg: None 表示正常完成；非 None 表示 fail-open 原因（如
          _shared.constants 不可导入或 scripts/governance/ 不存在），调用方
          应降级为 ReconcileResult(action="skip")。
    """
    shared_symbols = _get_shared_constants_symbols()
    if shared_symbols is None:
        # fail-open: _shared.constants 不可导入（环境问题）
        return [], "_shared.constants 不可导入，fail-open"

    gov_dir = project_root / "scripts" / "governance"
    if not gov_dir.exists():
        return [], "scripts/governance/ not found"

    violations: list[str] = []
    # glob all .py files recursively under scripts/governance/
    for py_file_path in glob.glob(str(gov_dir / "**" / "*.py"), recursive=True):
        # 转为相对路径（与 gate 的 py_file 格式一致：scripts/governance/...）
        rel = py_file_path.replace("\\", "/")
        idx = rel.find("scripts/governance/")
        if idx < 0:
            continue
        py_file = rel[idx:]
        if py_file in _EXEMPT_FILES:
            continue
        try:
            content = open(py_file_path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue  # fail-open: 文件不可读
        violations.extend(_scan_file_content(py_file, content, shared_symbols))

    return violations, None
