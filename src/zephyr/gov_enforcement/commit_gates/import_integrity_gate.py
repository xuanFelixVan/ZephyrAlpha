# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.import_integrity_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.security.access_control.session_concurrency (SessionRegistry, Phase 2.5 find_target_in_active_sessions 懒导入)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (gate registration)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件中 import 的目标模块在 main HEAD + staged 文件中不可解析时阻断（#ARCH-CROSS-COMMIT-ATOMICITY-001 治本）；fail-open（git 失败/文件不可读/ast 解析失败时放行）；wildcard import 跳过（导入集无法静态推断）；相对 import（from . / from ..）跳过（依赖文件位置上下文）；stdlib 与第三方库模块通过 importlib.util.find_spec 解析；项目内 zephyr. / scripts. 模块通过文件系统查找；Phase 2.5（#ARCH-CROSS-COMMIT-ATOMICITY-002）：阻断时自动（不依赖 AI 传 depends_on_sessions）检查目标模块是否在其他活跃 session held_files 中，若是追加友好提示"等待该 session merge"（fail-open：SessionRegistry 不可用时不追加提示，不阻断）；sys.path 注入识别（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 治本）：_extract_sys_path_dirs 提取 sys.path.insert/append 注入目录，_resolve_path_expr 启发式求值 4 种模式（直接 Path(__file__).resolve().parents[N] / str 包装变量 / 变量间接 _VAR.parent / next() 生成器向上搜索），_check_module_in_dirs 在注入目录中查找裸模块名（_shared/_common 等），找到则放行——320+ 脚本免疫，无需逐文件加 noqa 豁免（fail-open：无法求值的注入模式不提取该目录，由既有 noqa 逃生标记兜底）
# [MODIFY-GUARD] gate_id="IMPORT-INTEGRITY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git/ast/find_spec 失败降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_import_integrity_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 commit 事件触发（非 cron/manual）
"""
import_integrity_gate.py — IMPORT-INTEGRITY 门禁（悬空 import 硬阻断）

#ARCH-CROSS-COMMIT-ATOMICITY-001 治本（2026-07-20 立项）：

病根（第一性原理）
-----------------
ba40fa5b75（#ARCH-RUNCOMMAND-WINDOW-FLASH-001 Phase 1.5）在 git_commit_gateway.py
L154 添加了 from ...forged_gw_marker_gate import make_forged_gw_marker_gate，
但 forged_gw_marker_gate.py 36 分钟后才由 ce81f1077f 创建。两个 commit 之间
main 分支处于悬空 import 状态，触发 ModuleNotFoundError。

根因：跨 commit 原子性违规——同一功能涉及多文件被拆分到多个独立 commit，
每个单独 commit 都不完整。100% AI 开发场景下多 session 并发无协调，session A
引入 import（commit 早）、session B 创建文件（commit 晚）时 main 分支会出现
transient 悬空 import。

现有门禁盲区：
- UNDEFINED-NAME (F821)：检测"使用未定义符号"（NameError），不检测 import 的
  目标模块是否存在（ImportError）
- SCRIPTS-IMPORT-INTEGRITY：只检测 scripts/governance/ 对 _shared.constants 符号
  的使用，不通用
- 无任何 gate 检测"commit 引入了对不存在模块的 import"

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁（priority=107，紧接 UNDEFINED-NAME=106）：
  1. 对每个 staged .py 文件做 ast 解析，收集所有 Import / ImportFrom 节点
  2. 对每个 import 语句：
     (a) 相对 import（from . / from ..）跳过——依赖文件位置上下文
     (b) wildcard import（from X import *）跳过——导入集无法静态推断
     (c) stdlib / 第三方库：用 importlib.util.find_spec 解析，解析失败=违规
     (d) 项目内模块（zephyr.* / scripts.*）：将模块路径映射到文件系统路径，
         在 main HEAD（git show HEAD:path）+ staged 文件中查找，找不到=违规
  3. 硬阻断

设计权衡
--------
1. **fail-open 原则**：git 失败 / ast 解析失败 / find_spec 异常时不阻断 commit
   （与其他 gate 一致），记录 warning。
2. **相对 import 跳过**：`from . import X` / `from ..foo import Y` 依赖文件位置
   上下文，静态分析需推断包结构，复杂度高且易误报，权衡后跳过。
3. **wildcard import 跳过**：`from X import *` 无法静态推断导入了哪些符号，
   跳过避免假阳性（与 UNDEFINED-NAME / SCRIPTS-IMPORT-INTEGRITY 一致策略）。
4. **项目内模块用文件系统查找**：zephyr.* / scripts.* 模块通过将 `.` 替换为 `/`
   + `.py` 或 `/__init__.py` 在 main HEAD + staged 中查找，避免 import 副作用。
5. **第三方库用 find_spec**：stdlib 与 site-packages 模块通过 importlib 解析，
   失败=未安装=违规（AI 引入未声明依赖时阻断）。
6. **staged 文件优先**：先检查 staged 文件中是否有目标模块（同 commit 创建），
   再检查 main HEAD（已存在），两者都无才阻断。
7. **priority=107**：紧接 UNDEFINED-NAME=106，同属 import-related gate 组。

Phase 2.5 友好提示（#ARCH-CROSS-COMMIT-ATOMICITY-002，2026-07-21）
-------------------------------------------------------------------
阻断悬空 import 时，自动（不依赖 AI 传 depends_on_sessions）检查目标模块是否
在其他活跃 session held 的文件中。若是，追加友好提示——"目标模块在活跃 session
sess-B 的 held_files 中，可能正在创建中。修复：①等待该 session merge 后重试；
②同 commit 创建目标模块"——避免 AI 误判为"代码缺陷"反复修改（实际只需等待
依赖 session merge）。

设计权衡：
- 自动检测（不依赖 AI 传参）：符合 TRAE-068 第 6 层可预防性原则——100% AI 场景
  下君子协定失效（Phase 2 的 depends_on_sessions 参数 AI 不传即绕过），Phase 2.5
  通过 SessionRegistry.list_active() 自动发现活跃 session，零参数依赖。
- fail-open：SessionRegistry 不可用时不追加提示，不阻断（不引入新故障点）。
- 仅提示不阻断：阻断逻辑不变（Phase 1 硬阻断已覆盖），Phase 2.5 只优化错误消息。
- 排除自身：current_session_id 从 kwargs.session_id 获取，排除自身 held_files
  （自身 commit 的文件已在 staged_set，不会触发悬空 import，但 held_files 可能
  包含尚未 staged 的同模块文件，排除自身避免误报）。

Usage::

    from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
        make_import_integrity_gate,
    )
    registry.register(make_import_integrity_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: import_integrity_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: module_path 参数
#   fields: 参数 module_path，类型注解 str
#   code: import_integrity_gate.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: current_session_id 参数
#   fields: 参数 current_session_id，类型注解 str | None
#   code: import_integrity_gate.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: py_file 参数
#   fields: 参数 py_file，类型注解 str
#   code: import_integrity_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① find_target_in_active_sessions
#   name_en: find_target_in_active_sessions
#   intro: 检查目标模块是否在其他活跃 session 的 held_files 中（Phase 2.5 友好提示）。
#   desc: 检查目标模块是否在其他活跃 session 的 held_files 中（Phase 2.5 友好提示）。 Phase 2.5： GATE-IMPORT-INTEGRITY 阻断…；源码 L816-L865
#   inputs: project_root module_path current_session_id
#   outputs: list[tuple[str, str]]
# - id: A2
#   name_zh: ② scan_content_for_dangling_imports
#   name_en: scan_content_for_dangling_imports
#   intro: 扫描单文件内容的悬空 import（目标模块不可解析），返回违规消息列表（空=通过）。
#   desc: 扫描单文件内容的悬空 import（目标模块不可解析），返回违规消息列表（空=通过）。 Args: py_file: 文件相对路径（用于诊断消息） content: 文件内容 s…；源码 L868-L929
#   inputs: py_file content staged_files gateway
#   outputs: list[str]
# - id: A3
#   name_zh: ③ make_import_integrity_gate
#   name_en: make_import_integrity_gate
#   intro: 构造 IMPORT-INTEGRITY pre-commit 门禁（priority=107）。
#   desc: 构造 IMPORT-INTEGRITY pre-commit 门禁（priority=107）。 检测 staged scripts/governance/** + src/**…；源码 L932-L1007
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: list[tuple[str, str]]
#   name_en: list[tuple[str, str]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# - id: O2
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import ast
import importlib.util
import logging
import os
import re
import sys
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_noqa_lines,
    _get_staged_py_files,
    _make_noqa_pattern,
    _matches_any_prefix,
    _module_to_file_candidates,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = [
    "make_import_integrity_gate",
    "scan_content_for_dangling_imports",
    "find_target_in_active_sessions",
]

# 扫描范围：与 UNDEFINED-NAME 对齐
_SCAN_PREFIXES: tuple[str, ...] = ("scripts/governance/", "src/")

# 项目内模块前缀（用文件系统查找，避免 import 副作用）
_PROJECT_PREFIXES: tuple[str, ...] = ("zephyr.", "scripts.", "tests.")

# noqa 行级逃生：对标 bare-subprocess gate 模式
# 格式：`# noqa: import-integrity` + 2+ 空格 + reason（>=10 字符）
# 共享 helper（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）：正则由 _make_noqa_pattern 构造，
# 提取由 _diff_helpers._extract_noqa_lines 执行——消除与 bare_subprocess_gate 的逐字符克隆
_NOQA_PATTERN = _make_noqa_pattern("import-integrity")


def _is_relative_import(node: ast.Import | ast.ImportFrom) -> bool:
    """判断是否为相对 import（from . / from ..）。"""
    if isinstance(node, ast.Import):
        return False
    # ImportFrom.level > 0 表示相对 import（from . import X / from .. import Y）
    return node.level > 0


def _has_wildcard_import(node: ast.ImportFrom) -> bool:
    """判断 ImportFrom 是否含 wildcard（from X import *）。"""
    return any(alias.name == "*" for alias in node.names)


def _collect_imports(tree: ast.AST) -> list[tuple[int, str, bool]]:
    """收集模块级 import 语句，返回 (lineno, module_path, is_from) 列表。

    跳过：相对 import（依赖文件位置上下文）、wildcard import（导入集无法静态推断）。
    """
    imports: list[tuple[int, str, bool]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name, False))
        elif isinstance(node, ast.ImportFrom):
            if _is_relative_import(node):
                continue  # 跳过相对 import
            if _has_wildcard_import(node):
                continue  # 跳过 wildcard import
            if node.module is None:
                continue  # from . import X 已被相对 import 跳过
            imports.append((node.lineno, node.module, True))
    return imports


# _is_project_module / _module_to_file_candidates 已提取至 _diff_helpers
# （#ARCH-FORCE-MERGE-DEDUP-001 消除与 consumers_accuracy_gate 的逐字符克隆）
# 调用处直接使用 _matches_any_prefix(module_path, _PROJECT_PREFIXES) 和 _module_to_file_candidates(module_path)


def _check_project_module_resolvable(
    module_path: str,
    staged_files: set[str],
    gateway,
) -> bool:
    """检查项目内模块是否可在 staged + main HEAD 中解析。

    Args:
        module_path: 模块路径（如 zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate）
        staged_files: staged 文件路径集合（相对路径，正斜杠）
        gateway: GitCommitGateway 实例（用于 git show HEAD:path）

    Returns:
        True 如果模块可解析（staged 或 main HEAD 中存在），False 不可解析。
    """
    candidates = _module_to_file_candidates(module_path)
    # 1. 先检查 staged 文件（同 commit 创建的目标文件）
    for candidate in candidates:
        if candidate in staged_files:
            return True
    # 2. 再检查 main HEAD（已存在的目标文件）
    for candidate in candidates:
        try:
            result = gateway.run_git(["git", "show", f"HEAD:{candidate}"])
            if result.returncode == 0:
                return True
        except Exception:  # noqa: BLE001 — find_spec / git 失败 fail-open
            continue
    return False


def _check_external_module_resolvable(module_path: str) -> bool:
    """检查外部模块（stdlib / 第三方）是否可解析（importlib.util.find_spec）。

    Args:
        module_path: 模块路径（如 os / requests / numpy.array）

    Returns:
        True 如果模块可解析，False 不可解析。
    """
    try:
        # find_spec 支持子模块（如 os.path），取顶层模块的 spec 即可
        spec = importlib.util.find_spec(module_path)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False
    except Exception:  # noqa: BLE001 — find_spec 其他异常 fail-open
        return True  # fail-open：未知异常不阻断


# ── sys.path 注入目录提取（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 治本）──
# 病根：scripts/governance/ 下 320+ 脚本通过 sys.path.insert 动态注入
# _shared/_common 父目录，使 `from _shared import` / `from _common import`
# 在运行时可用。但静态 AST 分析无法解析这些裸模块名（不匹配
# _PROJECT_PREFIXES），被当作外部模块走 find_spec → site-packages 中不存在
# → 误判悬空 import → 硬阻断。
# 治本：门禁侧识别 sys.path 注入模式，在注入目录中查找目标模块文件，
# 找到则判定可解析——一次升级解决所有 320+ 文件，新文件自动免疫。


def _is_path_func(func: ast.AST) -> bool:
    """判断 func 是否为 Path 构造器调用形式。

    支持：
    - ``Path(...)``（``Name('Path')``）
    - ``pathlib.Path(...)``（``Attribute(value=Name('pathlib'), attr='Path')``）
    - ``__import__('pathlib').Path(...)``（``Attribute(value=Call(__import__), attr='Path')``）
    """
    if isinstance(func, ast.Name) and func.id == "Path":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "Path":
        value = func.value
        if isinstance(value, ast.Name) and value.id == "pathlib":
            return True
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "__import__"
            and value.args
            and isinstance(value.args[0], ast.Constant)
            and value.args[0].value == "pathlib"
        ):
            return True
    return False


def _is_path_file_bare(node: ast.AST) -> bool:
    """检查 node 是否为 ``Path(__file__)`` 调用（不含 ``.resolve()``）。

    支持三种 Path 形式：``Path`` / ``pathlib.Path`` / ``__import__('pathlib').Path``
    （见 ``_is_path_func``）。
    """
    if not isinstance(node, ast.Call):
        return False
    if not _is_path_func(node.func):
        return False
    return len(node.args) == 1 and isinstance(node.args[0], ast.Name) and node.args[0].id == "__file__"


def _is_path_file_resolve(node: ast.AST) -> bool:
    """检查 node 是否为 ``Path(__file__).resolve()`` 调用。

    AST 结构::

        Call(func=Attribute(attr='resolve', value=<Path(__file__)>), args=[])

    支持三种 Path 形式（见 ``_is_path_func``）。
    """
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "resolve"):
        return False
    return _is_path_file_bare(func.value)


def _extract_subscript_int(node: ast.Subscript) -> int | None:
    """从 Subscript 节点提取整数下标（兼容 Python 3.8 Index 包装）。"""
    slice_node = node.slice
    # Python 3.9+：slice 直接是表达式
    if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, int):
        return slice_node.value
    # Python 3.8 兼容：Index 包装
    if isinstance(slice_node, ast.Index):  # pragma: no cover (py3.8 only)
        inner = slice_node.value
        if isinstance(inner, ast.Constant) and isinstance(inner.value, int):
            return inner.value
    return None


def _resolve_path_object(
    node: ast.AST,
    file_abs: str,
    var_assigns: dict[str, ast.AST],
    _depth: int = 0,
) -> str | None:
    """将"路径对象"基底表达式解析为文件所在目录（file_dir）。

    ``Path(__file__).resolve()`` 指向文件本身，其 ``.parent`` / ``.parents[0]``
    均为 file_dir，故本函数对 resolve 调用统一返回 file_dir，作为后续
    ``.parent`` / ``.parents[N]`` / ``next(...)`` 的向上计数起点。

    支持：
    - ``Path(__file__).resolve()`` 直接形式 → file_dir
    - 指向上述的变量（1 层回溯）→ file_dir

    返回 None 表示无法识别（fail-open，不提取该目录）。
    """
    if _depth > 3:
        return None  # 防止变量链无限递归（允许 3 层变量链，覆盖 _VAR = REPO_ROOT; X = _VAR / "src" 同型）
    if _is_path_file_resolve(node):
        return os.path.dirname(file_abs)
    if _is_path_file_bare(node):
        return os.path.dirname(file_abs)
    # Path(VARIABLE) — 变量解析为字符串路径后原样返回（Path(str) ≈ str）
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id in var_assigns
    ):
        resolved = _resolve_path_expr(var_assigns[node.args[0].id], file_abs, var_assigns, _depth)
        if resolved is not None:
            return resolved
    if isinstance(node, ast.Name) and node.id in var_assigns:
        return _resolve_path_object(var_assigns[node.id], file_abs, var_assigns, _depth + 1)
    return None


def _extract_subdir_from_binop(binop: ast.BinOp) -> str | None:
    """从 BinOp Div 链取最左的字符串常量作为 subdir。

    ``p / "src" / "zephyr"`` → ``"src"``（最左常量）。取最左是为了向上搜索时
    命中含该子目录的最近祖先（如仓库根含 ``src/``），与运行时 ``next()`` 语义对齐。
    """
    # 递归到最左的 Name / Constant 形式
    if isinstance(binop.left, ast.BinOp) and isinstance(binop.left.op, ast.Div):
        return _extract_subdir_from_binop(binop.left)
    if (
        isinstance(binop.left, ast.Name)
        and isinstance(binop.right, ast.Constant)
        and isinstance(binop.right.value, str)
    ):
        return binop.right.value
    return None


def _extract_subdir_from_if(if_node: ast.AST) -> str | None:
    """从 comprehension 的 if 条件提取子目录名。

    识别：
    - ``(p / "subdir").exists()`` / ``(p / "subdir").is_dir()`` → ``"subdir"``
    - ``(p / "a" / "b").exists()`` → ``"a"``（链式取最左）
    - ``X and Y`` 组合 → 取首个可提取的子目录（覆盖
      ``(p/"scripts").is_dir() and (p/"src").is_dir()`` 同型模式）
    """
    # BoolOp(and) → 遍历取首个可提取
    if isinstance(if_node, ast.BoolOp) and isinstance(if_node.op, ast.And):
        for value in if_node.values:
            subdir = _extract_subdir_from_if(value)
            if subdir:
                return subdir
        return None
    if not (
        isinstance(if_node, ast.Call)
        and isinstance(if_node.func, ast.Attribute)
        and if_node.func.attr in ("exists", "is_dir")
    ):
        return None
    binop = if_node.func.value
    if not (isinstance(binop, ast.BinOp) and isinstance(binop.op, ast.Div)):
        return None
    return _extract_subdir_from_binop(binop)


def _try_resolve_next_parents_search(
    node: ast.AST,
    file_abs: str,
    var_assigns: dict[str, ast.AST],
) -> str | None:
    """启发式解析 ``next(p for p in <base>.parents if (p / "subdir").exists())``。

    项目中真实模式（generate_battle_map_diagram.py 等）::

        _THIS_FILE = Path(__file__).resolve()
        _GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
        sys.path.insert(0, _GOV_DIR)

    治本策略：从 <base> 所在目录（file_dir）向上查找首个含 ``<subdir>`` 子目录
    的祖先目录并返回。这与运行时 ``next()`` 语义一致。

    返回目录字符串或 None（非该模式 / 无法解析 → fail-open）。
    """
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "next"
        and node.args
        and isinstance(node.args[0], ast.GeneratorExp)
    ):
        return None
    gen = node.args[0]
    if len(gen.generators) != 1:
        return None
    comp = gen.generators[0]
    # iter 必须是 <base>.parents
    if not (isinstance(comp.iter, ast.Attribute) and comp.iter.attr == "parents"):
        return None
    # 用 _resolve_path_expr 而非 _resolve_path_object 解析 base，支持 base 为
    # .parent 链（如 _SCRIPT_DIR = Path(__file__).resolve().parent）的变量间接形式。
    # 注：base 差一级不影响结果——向上搜索首个含 subdir 的祖先目录，起点偏差由搜索兜底。
    base_dir = _resolve_path_expr(comp.iter.value, file_abs, var_assigns)
    if base_dir is None or not comp.ifs:
        return None
    subdir = _extract_subdir_from_if(comp.ifs[0])
    if not subdir:
        return None
    # 从 base_dir 向上查找首个含 subdir 的目录（含 base_dir 本身，对应 parents[0]）
    candidate = base_dir
    for _ in range(32):  # 防无限循环（目录树深度有限）
        if os.path.isdir(os.path.join(candidate, subdir)):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:  # 到达根目录
            return None
        candidate = parent
    return None


def _resolve_path_expr(
    node: ast.AST,
    file_abs: str,
    var_assigns: dict[str, ast.AST],
    _depth: int = 0,
) -> str | None:
    """启发式求值路径表达式，返回目录字符串或 None（无法求值）。

    支持的模式（覆盖项目中实际使用的 sys.path 注入模式）：
    - ``"字符串字面量"`` → 直接返回
    - ``str(EXPR)`` → 求值 EXPR
    - ``Path(__file__).resolve().parent`` → 文件所在目录
    - ``Path(__file__).resolve().parents[N]`` → 文件第 N 级父目录
    - ``_VAR = Path(__file__).resolve()`` 后 ``_VAR.parent`` / ``_VAR.parents[N]``
      → 变量间接形式（多层回溯，治本 #ARCH-IMPORT-INTEGRITY-SYSPATH-001）
    - ``next(p for p in <base>.parents if (p/"subdir").exists())`` → 向上搜索含
      subdir 的祖先目录（治本，覆盖 generate_battle_map_diagram.py 同型模式）
    - ``X / "subdir"`` → 路径拼接（BinOp Div，覆盖 str(Path(...).parent / "governance")
      等模式，治本 #ARCH-IMPORT-INTEGRITY-SYSPATH-001 BinOp 除法）
    - ``X.parent.parent`` → 嵌套 .parent 递归求值（每层取上一级目录）
    - 变量名 → 从 var_assigns 回溯求值（限 _depth ≤ 3 防无限递归）

    fail-open：无法识别的表达式返回 None（不提取该目录，不阻断 commit）。
    """
    if _depth > 3:
        return None  # 防止变量链无限递归（与 _resolve_path_object 对齐）

    # 字符串字面量
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    # str(EXPR) → 递归求值内部表达式
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "str" and node.args:
        return _resolve_path_expr(node.args[0], file_abs, var_assigns, _depth)

    # Path(EXPR) → 递归求值内部表达式（2026-08-20 波3 实证补齐：protected_paths_gate
    # ``gov_dir = Path(REPO_ROOT) / "scripts" / ...`` 模式——REPO_ROOT 经
    # _REPO_ROOT_IMPORT_MODULES 映射为 project_root 常量，Path() 包装此前无分支求值，
    # 致 str(gov_dir) 全链失败误报悬空；Path(__file__) 形态不受影响——__file__ 不在
    # var_assigns，Name 回溯失败返回 None，与旧行为一致）
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Path" and node.args:
        return _resolve_path_expr(node.args[0], file_abs, var_assigns, _depth)

    # X / "subdir" → 路径拼接（BinOp Div，治本 #ARCH-IMPORT-INTEGRITY-SYSPATH-001）
    # 覆盖 str(Path(__file__).resolve().parent / "governance") 等常见模式：
    # 左操作数递归求值为目录，右操作数求值为子目录字符串，os.path.join 拼接。
    # 左操作数可为 .parent 链 / 变量 / 另一个 BinOp Div（左结合链式 a / b / c）。
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _resolve_path_expr(node.left, file_abs, var_assigns, _depth)
        if left is None:
            return None
        right = _resolve_path_expr(node.right, file_abs, var_assigns, _depth)
        if not isinstance(right, str) or not right:
            return None
        return os.path.join(left, right)

    # 变量引用 → 回溯赋值（多层深度）
    if isinstance(node, ast.Name) and node.id in var_assigns:
        return _resolve_path_expr(var_assigns[node.id], file_abs, var_assigns, _depth + 1)

    # next(p for p in <base>.parents if (p / "subdir").exists()) — 启发式向上搜索
    next_result = _try_resolve_next_parents_search(node, file_abs, var_assigns)
    if next_result is not None:
        return next_result

    # <base>.parent → base 所在目录
    # base 可为：路径对象基底（Path(__file__).resolve() 等，_resolve_path_object 返回 file_dir）
    # 或另一个 .parent / .parents[N] 表达式（递归求值后取 dirname，支持 .parent.parent 嵌套）
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base_dir = _resolve_path_object(node.value, file_abs, var_assigns)
        if base_dir is not None:
            return base_dir
        # 嵌套 .parent（如 X.parent.parent）→ 递归求值 X 为目录后取上一级
        inner_dir = _resolve_path_expr(node.value, file_abs, var_assigns, _depth)
        if inner_dir is not None:
            return os.path.dirname(inner_dir)

    # <base>.parents[N] → base 所在目录向上 N 级
    # AST: Subscript(value=Attribute(attr='parents', value=<base>), slice=N)
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Attribute) and node.value.attr == "parents":
            base_dir = _resolve_path_object(node.value.value, file_abs, var_assigns)
            if base_dir is not None:
                n = _extract_subscript_int(node)
                if n is not None:
                    result = base_dir
                    for _ in range(n):
                        result = os.path.dirname(result)
                    return result

    # Path(__file__).resolve() 本身（保险，单独出现时指向文件目录）
    return _resolve_path_object(node, file_abs, var_assigns)


def _get_sys_path_arg(node: ast.Call) -> ast.AST | None:
    """如果是 sys.path.insert / sys.path.append 调用，返回路径参数 AST 节点。

    - ``sys.path.insert(0, X)`` → X（args[1]）
    - ``sys.path.append(X)`` → X（args[0]）

    非 sys.path 调用或参数不足返回 None。
    """
    func = node.func
    if not (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Attribute)
        and isinstance(func.value.value, ast.Name)
        and func.value.value.id == "sys"
        and func.value.attr == "path"
        and func.attr in ("insert", "append")
    ):
        return None
    if func.attr == "insert":
        if len(node.args) < 2:
            return None
        return node.args[1]
    if len(node.args) < 1:
        return None
    return node.args[0]


def _is_for_target_arg(p_arg: ast.AST, target_id: str) -> bool:
    """判断 sys.path.insert 的路径参数是否指向 for 循环变量 target_id。

    支持 ``_p``（Name）和 ``str(_p)``（Call str 包装）两种形式。
    """
    if isinstance(p_arg, ast.Name) and p_arg.id == target_id:
        return True
    return (
        isinstance(p_arg, ast.Call)
        and isinstance(p_arg.func, ast.Name)
        and p_arg.func.id == "str"
        and p_arg.args
        and isinstance(p_arg.args[0], ast.Name)
        and p_arg.args[0].id == target_id
    )


# 跨文件 import 的仓库根常量模块（SSoT 真源 zephyr.shared.io.paths.REPO_ROOT = find_repo_root()，
# 函数调用无法静态求值；_shared.constants 从 zephyr.shared.io.paths re-export）。
# 门禁识别后映射为 project_root（仓库根），使 str(REPO_ROOT / "src") 等可解析。
_REPO_ROOT_IMPORT_MODULES: tuple[str, ...] = (
    "_shared.constants",
    "zephyr.shared.io.paths",
)
_REPO_ROOT_IMPORT_NAMES: tuple[str, ...] = ("REPO_ROOT", "PROJECT_ROOT", "MAIN_REPO_ROOT")


def _extract_repo_root_while_var(test: ast.AST) -> str | None:
    """从 while 循环条件提取仓库根变量名（识别向上找 ``.git`` 模式）。

    匹配 ``while not (X / ".git").exists() and X != X.parent:`` 中的 X，
    该循环语义 = 向上查找含 ``.git`` 的祖先目录 = 仓库根 = project_root。
    """
    for node in ast.walk(test):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("exists", "is_dir")
            and isinstance(node.func.value, ast.BinOp)
            and isinstance(node.func.value.op, ast.Div)
            and isinstance(node.func.value.right, ast.Constant)
            and node.func.value.right.value == ".git"
            and isinstance(node.func.value.left, ast.Name)
        ):
            continue
        return node.func.value.left.id
    return None


def _extract_sys_path_dirs(tree: ast.AST, py_file: str, project_root: str | None = None) -> list[str]:
    """从 AST 中提取 ``sys.path.insert`` / ``sys.path.append`` 注入的目录路径。

    识别模式::

        sys.path.insert(0, X)   → X
        sys.path.append(X)      → X

    X 的求值委托 ``_resolve_path_expr``（启发式，无法求值则跳过——fail-open）。

    设计意图（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 治本）：
    scripts/governance/ 下 320+ 脚本通过 sys.path.insert 动态注入 _shared/
    _common 父目录，使 ``from _shared import`` / ``from _common import``
    在运行时可用。但静态 AST 分析无法解析这些裸模块名（不匹配
    _PROJECT_PREFIXES），被当作外部模块走 find_spec → site-packages 中不存在
    → 误判悬空 import → 硬阻断。本函数提取注入目录，供
    ``_check_module_in_dirs`` 在其中查找模块，避免对 320+ 文件逐个加
    import-integrity 豁免标记。

    Args:
        tree: 文件的 AST（已 ast.parse）。
        py_file: 文件相对路径（用于 ``Path(__file__)`` 求值）。

    Returns:
        注入目录的绝对路径列表（可能为空——无 sys.path 注入或无法求值）。
    """
    # 构建 var_assigns：模块级 Assign 优先（函数内 global 重新赋值不覆盖模块级初始值——
    # 模块级 sys.path 注入用模块级变量；函数内赋值常依赖运行时参数无法静态求值，
    # 如 _project_root 模块级 = Path(__file__)... 但函数内 global _project_root = Path(param)）
    var_assigns: dict[str, ast.AST] = {}
    module_level_vars: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    var_assigns[target.id] = stmt.value
                    module_level_vars.add(target.id)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id not in module_level_vars:
                    var_assigns[target.id] = node.value

    # 识别跨文件 import 的仓库根常量（REPO_ROOT 等），映射为 project_root。
    # 根因：REPO_ROOT 真源是 find_repo_root() 函数调用，无法静态求值；但语义=仓库根=project_root。
    if project_root:
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module not in _REPO_ROOT_IMPORT_MODULES:
                continue
            for alias in node.names:
                if alias.name in _REPO_ROOT_IMPORT_NAMES:
                    local_name = alias.asname or alias.name
                    # str() 包装（2026-08-20 波3 实证）：project_root 为 Path 对象时
                    # Constant(value=Path) 过不了 _resolve_path_expr 的 str 校验致全链失效
                    var_assigns[local_name] = ast.Constant(value=str(project_root))

    # 识别 while 循环向上找 .git 的仓库根模式
    # （_VAR = Path(__file__).resolve(); while not (_VAR / ".git").exists() ...: _VAR = _VAR.parent）
    # 语义=project_root，覆盖 migrate_sqlite_to_pg / repair 等同型模式
    if project_root:
        for node in ast.walk(tree):
            if not isinstance(node, ast.While):
                continue
            root_var = _extract_repo_root_while_var(node.test)
            if root_var:
                var_assigns[root_var] = ast.Constant(value=str(project_root))  # str 包装：Path 过不了 str 校验

    file_abs = os.path.abspath(py_file)
    dirs: list[str] = []
    # 已处理的 sys.path.insert/append Call（避免 for 批量分支与直接分支重复提取）
    handled_calls: set[int] = set()

    # 1) for X in (<tuple>): sys.path.insert(0, X) 批量注入模式
    #    scripts/governance/ 常见：for _p in (str(_REPO_ROOT), str(_SRC_DIR)): sys.path.insert(0, _p)
    #    _p 是循环变量（不在 var_assigns），需展开 tuple 各元素分别求值
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        if not (isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Tuple)):
            continue
        target_id = node.target.id
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Call):
                continue
            p_arg = _get_sys_path_arg(stmt)
            if p_arg is None:
                continue
            if not _is_for_target_arg(p_arg, target_id):
                continue
            # 解析 tuple 每个元素
            for elt in node.iter.elts:
                resolved = _resolve_path_expr(elt, file_abs, var_assigns)
                if resolved:
                    dirs.append(resolved)
            handled_calls.add(id(stmt))
            break  # 一个 for 内的 insert 只处理一次

    # 2) 直接 sys.path.insert(0, X) / sys.path.append(X) 模式
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if id(node) in handled_calls:
            continue
        path_arg = _get_sys_path_arg(node)
        if path_arg is None:
            continue
        resolved = _resolve_path_expr(path_arg, file_abs, var_assigns)
        if resolved:
            dirs.append(resolved)
    return dirs


def _check_module_in_dirs(module_path: str, dirs: list[str]) -> bool:
    """在给定目录列表中查找模块文件是否存在。

    对标 ``_module_to_file_candidates`` 但基于自定义目录（sys.path 注入目录）
    而非固定 ``src/`` 前缀。

    Args:
        module_path: 模块路径（如 ``_common`` / ``_shared.constants``）。
        dirs: 搜索目录列表（绝对路径）。

    Returns:
        True 如果模块在任一目录中以 ``.py`` 或 ``__init__.py`` 形式存在。
    """
    parts = module_path.split(".")
    for d in dirs:
        base = os.path.join(d, *parts)
        if os.path.isfile(base + ".py"):
            return True
        if os.path.isfile(os.path.join(base, "__init__.py")):
            return True
    return False


def find_target_in_active_sessions(
    project_root: Path,
    module_path: str,
    current_session_id: str | None = None,
) -> list[tuple[str, str]]:
    """检查目标模块是否在其他活跃 session 的 held_files 中（Phase 2.5 友好提示）。

    #ARCH-CROSS-COMMIT-ATOMICITY-002 Phase 2.5：
    GATE-IMPORT-INTEGRITY 阻断悬空 import 时，自动（不依赖 AI 传 depends_on_sessions）
    检查目标模块是否在其他活跃 session held 的文件中。若是，追加友好提示——
    "目标模块在活跃 session sess-B 的 held_files 中，可能正在创建中"——
    避免 AI 误判为"代码缺陷"反复修改（实际只需等待依赖 session merge）。

    Args:
        project_root: 项目根目录（用于构造 SessionRegistry）
        module_path: 模块路径（如 zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate）
        current_session_id: 当前 commit 的 session_id（排除自身；自身 commit 的文件
            已在 staged_set，不会触发悬空 import，但 held_files 可能包含尚未 staged
            的同模块文件，排除自身避免误报）

    Returns:
        [(session_id, matched_candidate_path), ...] 列表。空列表=未在其他 session 中
        或 SessionRegistry 不可用（fail-open）。
    """
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        registry = SessionRegistry(project_root=project_root)
        active_sessions = registry.list_active()
        candidates = _module_to_file_candidates(module_path)
        hits: list[tuple[str, str]] = []
        for info in active_sessions:
            if current_session_id and info.session_id == current_session_id:
                continue  # 排除自身
            for held_file in info.held_files:
                # held_file 是绝对路径（_normalize_file_path 归一化），candidates 是
                # 相对路径（src/zephyr/... 或 zephyr/...）。用 endswith 匹配（跨平台
                # 路径分隔符归一化为正斜杠）。
                held_norm = held_file.replace("\\", "/")
                for candidate in candidates:
                    if held_norm.endswith(candidate):
                        hits.append((info.session_id, candidate))
                        break
        return hits
    except Exception as e:  # noqa: BLE001 — fail-open
        logger.debug(
            "IMPORT-INTEGRITY: find_target_in_active_sessions fail-open: %s",
            e,
        )
        return []


def scan_content_for_dangling_imports(
    py_file: str,
    content: str,
    staged_files: set[str],
    gateway,
) -> list[str]:
    """扫描单文件内容的悬空 import（目标模块不可解析），返回违规消息列表（空=通过）。

    Args:
        py_file: 文件相对路径（用于诊断消息）
        content: 文件内容
        staged_files: staged 文件路径集合（相对路径，正斜杠）
        gateway: GitCommitGateway 实例（用于 git show HEAD:path）

    Returns:
        违规消息列表（空=通过）。
    """
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        return []  # fail-open：语法错误由其他阶段检测

    imports = _collect_imports(tree)
    noqa_lines = _extract_noqa_lines(content, _NOQA_PATTERN)
    # #ARCH-IMPORT-INTEGRITY-SYSPATH-001 治本：提取 sys.path 注入目录，
    # 使 from _shared / from _common 等动态加载模块可被解析（320+ 文件免疫）
    sys_path_dirs = _extract_sys_path_dirs(tree, py_file, getattr(gateway, "project_root", None))
    # 隐式 script-dir 解析（2026-08-20 波3 实证 18+ 文件误报补齐）：
    # ①CPython 直接执行语义——python scripts/x/y.py 时脚本自身目录自动入 sys.path[0]，
    #   from _shared/_common/同目录模块 无显式注入运行时亦可解析；
    # ②scripts/governance/** 额外补 scripts/governance（_shared/_common 唯一真源所在地，
    #   项目入口脚本 run_gate_chain/sync_panorama_module 均以该目录为 script-dir 运行，
    #   嵌套脚本经入口导入时运行时可达）。
    # 安全边界：_check_module_in_dirs 校验模块文件真实存在才放行，幻觉模块名仍阻断。
    _root = getattr(gateway, "project_root", None)
    _norm_file = py_file.replace("\\", "/")
    if _root and _norm_file.startswith("scripts/"):
        _implicit = [os.path.join(str(_root), os.path.dirname(_norm_file))]
        if _norm_file.startswith("scripts/governance/"):
            _implicit.append(os.path.join(str(_root), "scripts", "governance"))
        for _d in _implicit:
            if _d not in sys_path_dirs:
                sys_path_dirs.append(_d)
    violations: list[str] = []
    for lineno, module_path, _is_from in imports:
        if lineno in noqa_lines:
            continue  # 行级 noqa 逃生
        if _matches_any_prefix(module_path, _PROJECT_PREFIXES):
            if not _check_project_module_resolvable(module_path, staged_files, gateway):
                violations.append(
                    f"  {py_file}:{lineno}: dangling import '{module_path}' "
                    f"(project module not resolvable in staged files or main HEAD)"
                )
        elif sys_path_dirs and _check_module_in_dirs(module_path, sys_path_dirs):
            continue  # 模块在 sys.path 注入目录中存在——可解析（治本）
        else:
            if not _check_external_module_resolvable(module_path):
                violations.append(
                    f"  {py_file}:{lineno}: dangling import '{module_path}' "
                    f"(external module not installed / not found by importlib)"
                )
    return violations


def make_import_integrity_gate() -> GateSpec:
    """构造 IMPORT-INTEGRITY pre-commit 门禁（priority=107）。

    检测 staged scripts/governance/** + src/**.py 的悬空 import（目标模块不可解析），
    硬阻断。fail-open：无 staged 文件/git 失败/文件不可读/ast 解析失败时放行。

    #ARCH-CROSS-COMMIT-ATOMICITY-001 治本（2026-07-20）：
    防止 ba40fa5b75 同型违规——commit 引入了对不存在模块的 import。
    """

    def _check(gateway, _files: list[str], **_kwargs) -> tuple[bool, str]:
        staged = _get_staged_py_files(gateway, "IMPORT-INTEGRITY")
        if not staged:
            return True, ""

        staged_set = set(staged)
        violations: list[str] = []
        for py_file in staged:
            if not py_file.startswith(_SCAN_PREFIXES):
                continue
            # 排除 _archive 目录（归档一次性代码不参与扫描——同族先例：undefined_name_gate
            # 裁定#E / bare_sql_gate / reconciler_file_ops_gate 同口径；2026-08-20 波3 实证
            # format 重排归档脚本存量 import 伪"新增"致误报 analyze_orphan_consumers 等 4 处）
            if "_archive" in py_file:
                continue
            content = _read_staged_file(gateway, py_file)
            if content is None:
                continue  # fail-open: 文件不可读（git show 失败）
            violations.extend(scan_content_for_dangling_imports(py_file, content, staged_set, gateway))

        if violations:
            # Phase 2.5（#ARCH-CROSS-COMMIT-ATOMICITY-002）：
            # 阻断时自动（不依赖 AI 传 depends_on_sessions）检查目标模块是否在
            # 其他活跃 session held 的文件中。若是，追加友好提示——避免 AI 误判
            # 为"代码缺陷"反复修改（实际只需等待依赖 session merge）。
            current_session_id = _kwargs.get("session_id")
            _project_root = getattr(gateway, "project_root", None)
            enhanced: list[str] = []
            for v in violations:
                m = re.search(r"dangling import '([^']+)'", v)
                if m and _project_root is not None:
                    _mod = m.group(1)
                    hits = find_target_in_active_sessions(
                        _project_root,
                        _mod,
                        current_session_id,
                    )
                    if hits:
                        hit_str = "; ".join(f"sess={sid} held={cand}" for sid, cand in hits)
                        v = (
                            v + f"  [Phase 2.5 hint: 目标模块在活跃 session 的 "
                            f"held_files 中 ({hit_str})。修复：①等待该 session "
                            f"merge 后重试；②同 commit 创建目标模块]"
                        )
                enhanced.append(v)

            detail = (
                "IMPORT-INTEGRITY: 悬空 import（目标模块不可解析，"
                "#ARCH-CROSS-COMMIT-ATOMICITY-001 治本）\n"
                "  病根：commit 引入了对不存在模块的 import——跨 commit 原子性违规\n"
                "  （import 语句先行于目标文件创建，多 session 并发无协调）。\n"
                "  修复：①将 import 与目标文件放同 commit；\n"
                "        ②若目标文件已存在于其他分支，先 merge 再 import；\n"
                "        ③若为外部库，先 pip install 并更新 requirements。\n"
                + "\n".join(enhanced[:50])
                + (f"\n  ...(+{len(enhanced) - 50} more)" if len(enhanced) > 50 else "")
            )
            logger.error("IMPORT-INTEGRITY gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(
        gate_id="IMPORT-INTEGRITY",
        check=_check,
        priority=107,
    )
