#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_CHECK_ANY_ABUSE | scripts/governance/d7_code/check_any_abuse.py | §
# [MODULE] scripts.governance.d7_code.check_any_abuse
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(ast/pathlib/dataclasses/argparse/re)
# [CONSUMERS] .pre-commit-config.yaml gate-any-abuse
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 实现，不依赖 ruff/mypy
# [MODIFY-GUARD] 修改阈值需同步更新 AGENTS.md §8 GATE-ANY-ABUSE 条目
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=clean / 1=--ci violations / 2=src dir missing
# [TESTS] 手动验证: R70 基线 ANY-1=462 / ANY-2=172 / 总计 634；#ARCH-ANY-GOVERNANCE-001 Phase 2 清零至 0
# [A_module] module_id=MOD-GOV_CHECK_ANY_ABUSE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
类型注解 Any 滥用扫描器 — 5.145 维度防御门闸（R70 引入，#ARCH-ANY-GOVERNANCE-001 Phase 3 升级为 commit 阻断）。

检测函数签名中的"裸 Any 滥用"——AI 偷懒写法的典型模式：
  - ANY-1 函数参数类型为裸 Any（非 dict[str, Any] / list[Any] 等容器型）
  - ANY-2 函数返回值类型为裸 Any（非 dict[str, Any] 等容器型）

豁免规则（合理用法不报）：
  - dict[str, Any] / dict[str, Any] | None 等容器型 Any（配置字典是合理用法）
  - list[Any] / tuple[Any, ...] 等容器型
  - Callable[..., Any]（回调返回值多变，合理）
  - TYPE_CHECKING 块内的 Any（仅类型检查上下文）
  - **kwargs: Any（兼容旧 API 的合理模式）
  - stub 文件（.pyi）
  - __init__ 构造函数的返回值（无返回值注解不报）
  - `# noqa: any-abuse` 行级标记（Phase 3：合理 Any 逃生通道，需附理由）

病根对标：
  - 5.145.10/11/13-26 Any 滥用 = AI 偷懒的默认写法
  - 战略裁定1：新发现违规转化为 AST 门禁，不再加规则文档

使用：
  python scripts/governance/d7_code/check_any_abuse.py [--src DIR] [--ci] [--quiet] [file1 file2 ...]

退出码：
  0 = clean / warn-only 模式下有违规也返回 0
  1 = --ci 模式下检测到违规（pre-commit hard block）
  2 = src 目录缺失或参数错误

设计原则（对标 scan_debt.py）：
  - 纯 stdlib（ast + pathlib + re），不依赖 ruff/mypy 是否安装
  - 增量扫描：传文件列表时只扫这些文件；不传则扫 src/zephyr/
  - 误报优先：宁可放过，不可误伤 commit 工作流
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 类型注解 Any 滥用扫描器 — 5.145 维度防御门闸（R70 引入，#ARCH-ANY-GOVERNANCE-001 Phase 3
  升级为 commit 阻断）。
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# bootstrap sys.path for _shared.staged_files import（轻量模块，无 psycopg2 传递依赖）
# 治本（2026-08-03）：替代原 23 行内联 git diff 重复代码，统一使用 iter_staged_files SSoT
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
import yaml
from _shared.staged_files import iter_staged_files

# ── EXIT 常量（对标 _shared/constants.py，避免 import 链引入 psycopg2）─────
# check_any_abuse.py 是 commit-time gate，必须零重依赖（仅 stdlib + PyYAML），
# 禁止 from _shared.constants import（会间接 import psycopg2 导致 gate 崩溃）
EXIT_PASS = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

# ── 豁免模式 ──────────────────────────────────────────────────────────────
# 这些 Any 用法是合理的，不报违规。

# 容器型 Any：dict[str, Any] / list[Any] / tuple[Any, ...] / set[Any]
_CONTAINER_TYPES = {"dict", "list", "tuple", "set", "frozenset"}

# Callable[..., Any] / Callable[[X], Any] 回调返回值
_CALLABLE_TYPES = {"Callable", "callable"}

# **kwargs: Any 兼容旧 API
_KWARGS_ANY_OK = True

# 参考 noqa_exempt_registry.yaml SSoT 路径（真源唯一，禁止硬编码 marker 字符串）
_NOQA_REGISTRY = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "noqa_exempt_registry.yaml"
)
_NOQA_ANY_ABUSE_RE: re.Pattern[str] | None = None  # 懒加载缓存


def _load_yaml_safe(path: Path) -> dict:
    """最小化 YAML 加载（纯 PyYAML，避免 _shared.yaml_utils 引入 psycopg2）。"""
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


@dataclass
class AnyViolation:
    """单条 Any 滥用违规记录。"""

    file: str
    line: int
    col: int
    kind: str  # "ANY-1" (参数) / "ANY-2" (返回值)
    function: str
    annotation: str  # 原始注解文本
    detail: str

    def format(self) -> str:
        """格式化为可读字符串。"""
        return (
            f"{self.file}:{self.line}:{self.col}: "
            f"{self.kind} {self.function} — {self.detail} "
            f"(annotation: {self.annotation})"
        )


def _annotation_to_str(node: ast.expr | None) -> str:
    """AST 注解节点转字符串（用于报告）。"""
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:  # noqa: BLE001
        return ast.dump(node)


def _is_bare_any(node: ast.expr | None) -> bool:
    """判断注解节点是否是"裸 Any"（非容器型）。

    裸 Any = Any / Any | None / Optional[Any]
    非 裸 Any = dict[str, Any] / list[Any] / Callable[..., Any] 等
    """
    if node is None:
        return False

    # 直接 Any
    if isinstance(node, ast.Name) and node.id == "Any":
        return True

    # Any | None / None | Any (PEP 604 联合类型)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _is_bare_any(node.left) or _is_bare_any(node.right)

    # Optional[Any] / Union[Any, X] —— Subscript
    if isinstance(node, ast.Subscript):
        value = node.value
        # Optional[Any] = typing.Optional[Any]
        if isinstance(value, ast.Name) and value.id == "Optional":
            slc = node.slice
            if isinstance(slc, ast.Name) and slc.id == "Any":
                return True
            # Optional[Union[Any, X]] 递归
            if isinstance(slc, ast.Tuple):
                return any(_is_bare_any(elt) for elt in slc.elts)
            return False
        # dict[str, Any] / list[Any] / Callable[..., Any] 等容器型 —— 不算裸 Any
        if isinstance(value, ast.Name) and value.id in _CONTAINER_TYPES:
            return False
        if isinstance(value, ast.Name) and value.id in _CALLABLE_TYPES:
            return False
        # typing.Dict[str, Any] 等 typing 模块容器
        if isinstance(value, ast.Attribute) and value.attr in _CONTAINER_TYPES:
            return False
        if isinstance(value, ast.Attribute) and value.attr in _CALLABLE_TYPES:
            return False
        # Union[Any, str] —— 检查 slice
        if isinstance(value, ast.Name) and value.id == "Union":
            slc = node.slice
            if isinstance(slc, ast.Tuple):
                # Union 全是 Any 才算裸 Any（如 Union[Any, None] = Any）
                return all(
                    (isinstance(elt, ast.Name) and elt.id == "Any")
                    for elt in slc.elts
                )
            return isinstance(slc, ast.Name) and slc.id == "Any"
        return False

    return False


def _in_type_checking(node: ast.AST, parents: list[ast.AST]) -> bool:
    """判断节点是否在 TYPE_CHECKING if 块内。"""
    # 简化实现：通过父节点链查找 if TYPE_CHECKING
    for parent in reversed(parents):
        if isinstance(parent, ast.If):
            test = parent.test
            if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                return True
    return False


def _scan_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filepath: str,
    parents: list[ast.AST],
) -> list[AnyViolation]:
    """扫描单个函数的参数和返回值注解。"""
    violations: list[AnyViolation] = []
    func_name = node.name

    # 跳过 TYPE_CHECKING 块内的函数（仅类型检查上下文）
    if _in_type_checking(node, parents):
        return violations

    # ── ANY-1: 参数裸 Any ──
    args = node.args
    # 位置参数（含 self/cls 之后的）
    for arg in args.args:
        # 跳过 self/cls
        if arg.arg in ("self", "cls"):
            continue
        if _is_bare_any(arg.annotation):
            # **kwargs: Any 豁免
            # (args.args 不含 **kwargs，kwonlyargs 才有)
            violations.append(AnyViolation(
                file=filepath,
                line=arg.lineno,
                col=arg.col_offset,
                kind="ANY-1",
                function=func_name,
                annotation=_annotation_to_str(arg.annotation),
                detail=f"参数 '{arg.arg}' 使用裸 Any，应替换为具体类型",
            ))

    # keyword-only 参数
    for arg in args.kwonlyargs:
        if _is_bare_any(arg.annotation):
            violations.append(AnyViolation(
                file=filepath,
                line=arg.lineno,
                col=arg.col_offset,
                kind="ANY-1",
                function=func_name,
                annotation=_annotation_to_str(arg.annotation),
                detail=f"关键字参数 '{arg.arg}' 使用裸 Any，应替换为具体类型",
            ))

    # *args: Any —— 豁免（兼容旧 API，对标 **kwargs）
    if args.vararg and _is_bare_any(args.vararg.annotation):
        # *args: Any 合理，不报
        pass

    # **kwargs: Any —— 豁免
    if args.kwarg and _is_bare_any(args.kwarg.annotation):
        # **kwargs: Any 合理，不报
        pass

    # ── ANY-2: 返回值裸 Any ──
    # 跳过 __init__ / __post_init__ 等无返回值的 dunder
    if func_name.startswith("__") and func_name.endswith("__"):
        # __init__ 等通常无返回值注解，有也不报
        pass
    elif _is_bare_any(node.returns):
        violations.append(AnyViolation(
            file=filepath,
            line=node.lineno,
            col=node.col_offset,
            kind="ANY-2",
            function=func_name,
            annotation=_annotation_to_str(node.returns),
            detail="返回值使用裸 Any，应替换为具体类型",
        ))

    return violations


class _FunctionScanner(ast.NodeVisitor):
    """AST 遍历器——O(n) 收集函数签名 Any 滥用违规。

    维护父节点栈用于 TYPE_CHECKING 块检测。
    替代原 O(n²) 嵌套 ast.walk 方案（审查修复 2026-07-06）。
    """

    def __init__(self, filepath: str) -> None:
        """__init__ implementation."""
        self.filepath = filepath
        self.violations: list[AnyViolation] = []
        self._stack: list[ast.AST] = []

    def _scan_and_descend(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """扫描函数签名，然后继续遍历子节点。"""
        self.violations.extend(_scan_function(node, self.filepath, self._stack))
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """visit_FunctionDef implementation."""
        self._scan_and_descend(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """visit_AsyncFunctionDef implementation."""
        self._scan_and_descend(node)

    def visit_If(self, node: ast.If) -> None:
        """visit_If implementation."""
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """visit_ClassDef implementation."""
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()


def scan_file(filepath: Path) -> list[AnyViolation]:
    """扫描单个 .py 文件的 Any 滥用。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [AnyViolation(
            file=str(filepath),
            line=0,
            col=0,
            kind="ERROR",
            function="",
            annotation="",
            detail=f"无法读取文件: {e}",
        )]

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as e:
        return [AnyViolation(
            file=str(filepath),
            line=e.lineno or 0,
            col=e.offset or 0,
            kind="ERROR",
            function="",
            annotation="",
            detail=f"语法错误: {e.msg}",
        )]

    rel_path = str(filepath).replace("\\", "/")
    scanner = _FunctionScanner(rel_path)
    scanner.visit(tree)
    violations = scanner.violations

    # "noqa: any-abuse" 行级豁免过滤（#ARCH-ANY-GOVERNANCE-001 Phase 3）
    # 标记所在行的违规被豁免，需附理由（格式：noqa: any-abuse + 豁免理由，详见 noqa_exempt_registry.yaml）
    if violations:
        noqa_lines = _collect_noqa_any_abuse_lines(content)
        if noqa_lines:
            violations = [
                v for v in violations
                if v.kind not in ("ANY-1", "ANY-2") or v.line not in noqa_lines
            ]

    return violations


def _get_noqa_any_abuse_re() -> re.Pattern[str] | None:
    """从 noqa_exempt_registry.yaml 动态加载 any-abuse marker（SSoT，禁止硬编码）。

    #ARCH-ANY-GOVERNANCE-001 Phase 3 + 审查 P2 修复：
    marker 字符串真源唯一在 noqa_exempt_registry.yaml，本函数动态加载并构建正则。
    fail-open：registry 加载失败或 marker 不存在时返回 None（不阻断检测器运行）。
    """
    global _NOQA_ANY_ABUSE_RE
    if _NOQA_ANY_ABUSE_RE is not None:
        return _NOQA_ANY_ABUSE_RE
    try:
        data = _load_yaml_safe(_NOQA_REGISTRY)
        for m in (data.get("markers") or []) if data else []:
            if m.get("marker") == "any-abuse":
                _NOQA_ANY_ABUSE_RE = re.compile(r"#\s*noqa:\s*any-abuse\b")
                return _NOQA_ANY_ABUSE_RE
        # marker 未登记在 registry
        return None
    except Exception:  # noqa: BLE001
        return None


def _collect_noqa_any_abuse_lines(content: str) -> set[int]:
    """收集 content 中所有含 `# noqa: any-abuse` 标记的行号（1-based）。

    #ARCH-ANY-GOVERNANCE-001 Phase 3：行级豁免机制，
    marker 真源在 noqa_exempt_registry.yaml（动态加载，禁止硬编码）。
    """
    lines: set[int] = set()
    pattern = _get_noqa_any_abuse_re()
    if pattern is None:
        return lines  # registry 不可达或 marker 未登记 → 无豁免
    for idx, line in enumerate(content.splitlines(), start=1):
        if pattern.search(line):
            lines.add(idx)
    return lines


def scan_directory(src_dir: Path, files: list[Path] | None = None) -> list[AnyViolation]:
    """扫描目录或文件列表。"""
    if files:
        py_files = [f for f in files if f.suffix == ".py" and f.exists()]
    else:
        py_files = list(src_dir.rglob("*.py"))
        # 排除 __pycache__ / _archive / .aidrafts
        py_files = [
            f for f in py_files
            if "__pycache__" not in f.parts
            and "_archive" not in f.parts
            and ".aidrafts" not in f.parts
        ]

    all_violations: list[AnyViolation] = []
    for py_file in py_files:
        all_violations.extend(scan_file(py_file))

    return all_violations


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。

    退出码：
      0 = clean / warn-only 有违规也返回 0
      1 = --ci 模式下检测到违规
      2 = 参数错误或目录缺失
    """
    parser = argparse.ArgumentParser(
        description="类型注解 Any 滥用扫描器（5.145 维度门闸）",
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "src" / "zephyr",
        help="扫描目录（默认 src/zephyr/）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式：检测到违规返回 exit 1（pre-commit hard block）",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式：只输出违规，不输出摘要",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="变更检测：只扫 staged .py（pre-commit，替代全量 3.8s→亚秒）",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="增量扫描：只检查指定文件（pre-commit 传入 staged 文件）",
    )
    args = parser.parse_args(argv)

    # 增量模式：传入文件列表
    file_list: list[Path] | None = None
    if args.files:
        file_list = [Path(f) for f in args.files]
        # 过滤：只扫 src/zephyr/ 下的 .py
        src_prefix = str(args.src.resolve()).replace("\\", "/")
        file_list = [
            f for f in file_list
            if f.suffix == ".py"
            and str(f.resolve()).replace("\\", "/").startswith(src_prefix)
        ]
        if not file_list:
            print("[check_any_abuse] 无 src/zephyr/ 下的 .py 文件，跳过")
            return EXIT_PASS
    elif args.staged:
            # 变更检测：使用共享 iter_staged_files（真源 _shared/staged_files.py，轻量模块无 psycopg2）
            # 治本（2026-08-03）：消除 23 行内联 git diff 重复代码，统一 SSoT
            file_list = iter_staged_files(
                extensions=frozenset({".py"}),
                path_prefix="src/zephyr/",
            )
            if not file_list:
                print("[check_any_abuse] 无 staged src/zephyr/ .py 文件，跳过")
                return EXIT_PASS
    if not args.src.exists() and not file_list:
        print(f"[check_any_abuse] 错误：src 目录不存在: {args.src}", file=sys.stderr)
        return EXIT_ERROR
    violations = scan_directory(args.src, file_list)

    # 过滤 ERROR 类型（文件读取/语法错误单独报告）
    real_violations = [v for v in violations if v.kind in ("ANY-1", "ANY-2")]
    errors = [v for v in violations if v.kind == "ERROR"]

    if errors:
        for e in errors:
            print(f"ERROR: {e.format()}", file=sys.stderr)

    if not real_violations:
        if not args.quiet:
            print("[check_any_abuse] clean — 无函数签名裸 Any 滥用")
        return EXIT_PASS
    # 输出违规
    for v in real_violations:
        print(v.format())

    # 摘要
    if not args.quiet:
        any1_count = sum(1 for v in real_violations if v.kind == "ANY-1")
        any2_count = sum(1 for v in real_violations if v.kind == "ANY-2")
        print(
            f"\n[check_any_abuse] 发现 {len(real_violations)} 处违规: "
            f"ANY-1(参数裸Any)={any1_count} + ANY-2(返回值裸Any)={any2_count}"
        )
        print(
            "[check_any_abuse] 修复指南: 函数参数/返回值不应使用裸 Any，"
            "应替换为具体类型或 Protocol。dict[str,Any] 等容器型 Any 豁免。"
        )

    if args.ci:
        return EXIT_FINDINGS
    return EXIT_PASS
if __name__ == "__main__":
    sys.exit(main())
