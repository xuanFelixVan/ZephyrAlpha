#!/usr/bin/env python
# [BLUEPRINT] N/A | scripts/governance/d7_code/scan_debt.py | §
# [MODULE] scripts.governance.d7_code.scan_debt
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib(ast/pathlib/dataclasses/argparse)
# [CONSUMERS] .pre-commit-config.yaml gate-debt-bridge
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 纯 stdlib 实现，不依赖 ruff/mypy
# [MODIFY-GUARD] 修改阈值需同步更新 AGENTS.md §8 GATE-DEBT-BRIDGE 条目
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=clean/warn-only / 1=--ci violations / 2=src dir missing
# [TESTS] 手动验证: R67 基线 DEBT-1=0/DEBT-2=13/DEBT-3=0
# [TTL] permanent
"""
架构债务扫描器 — 5.96 维度防御门闸（R67 引入）。

检测 3 类"AI 容易复发的代码异味"：
  - DEBT-1 dataclass 布尔字段冗余：@dataclass 含 action/role 字段 + ≥2 个派生布尔字段
    （典型病根：should_rollback/retry_allowed/forward_fix_allowed 与 action 完全冗余，
     互斥动作的布尔组合可能不一致 → 5.96.2 病根）
  - DEBT-2 函数布尔参数蔓延：函数（含方法）含 ≥3 个 bool 参数（不含 self/cls）
    （典型病根：_calculate_trust(git_ok, test_ok, audit_ok) → 5.96.3 病根）
  - DEBT-3 action+should_* 共存：任意 class 含 action: str + should_*/is_*/_allowed: bool 字段
    （DEBT-1 的非 dataclass 兜底版，检测普通 class 的同模式）

使用：
  python scripts/governance/d7_code/scan_debt.py [--src DIR] [--ci] [--quiet]

退出码：
  0 = clean / warn-only 模式下有违规也返回 0
  1 = --ci 模式下检测到违规（pre-commit hard block）

设计原则：
  - 纯 stdlib（ast + pathlib），不依赖 ruff/mypy 是否安装
  - 增量扫描 staged 文件（pre-commit 集成时由调用方传文件列表）
  - 误报优先：宁可放过，不可误伤 commit 工作流
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# ── 阈值（可调）──────────────────────────────────────────────────────────
MAX_BOOL_PARAMS = 3          # DEBT-2: 函数含 ≥3 个 bool 参数即报警
MIN_REDUNDANT_BOOL_FIELDS = 2  # DEBT-1/3: ≥2 个派生布尔字段才报警
ACTION_FIELD_NAMES = {"action", "role", "kind", "type", "category"}
BOOL_FIELD_PREFIXES = ("should_", "is_", "has_", "can_", "allow_", "do_")
BOOL_FIELD_SUFFIXES = ("_allowed", "_enabled", "_required")


# ── 违规记录 ─────────────────────────────────────────────────────────────
@dataclass
class DebtViolation:
    code: str        # DEBT-1 / DEBT-2 / DEBT-3
    file: str
    line: int
    symbol: str      # 类名或函数名
    detail: str

    def format(self) -> str:
        return f"{self.code} {self.file}:{self.line} [{self.symbol}] {self.detail}"


# ── 工具函数 ─────────────────────────────────────────────────────────────
def _is_bool_annotation(ann: ast.AST | None) -> bool:
    """判断注解是否为 bool（含 bool | None / Optional[bool]）。"""
    if ann is None:
        return False
    # 直接 bool
    if isinstance(ann, ast.Name) and ann.id == "bool":
        return True
    # bool | None (PEP 604)
    if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
        return _is_bool_annotation(ann.left) or _is_bool_annotation(ann.right)
    # Optional[bool] / Union[bool, None]
    if isinstance(ann, ast.Subscript):
        slc = ann.slice
        if isinstance(slc, ast.Tuple):
            return any(_is_bool_annotation(e) for e in slc.elts)
        return _is_bool_annotation(slc)
    return False


def _is_action_field(name: str, ann: ast.AST | None) -> bool:
    """action/role/kind/type/category 字段，类型为 str 或 Enum。"""
    if name.lower() not in ACTION_FIELD_NAMES:
        return False
    # str 或 Enum（Name 或 Subscript）
    if ann is None:
        return True  # 无注解也视为 action 字段（保守）
    if isinstance(ann, ast.Name):
        return True  # str 或 Enum 类名
    return True  # 保守：所有注解都视为 action 字段


def _is_bool_flag_field(name: str, ann: ast.AST | None) -> bool:
    """派生布尔字段：should_*/is_*/has_*/can_*/allow_*/do_* 或 *_allowed/*_enabled/*_required。"""
    if not _is_bool_annotation(ann):
        # 无注解但命名匹配也视为可疑（保守放过：必须有 bool 注解或默认值是 True/False）
        return False
    name_lower = name.lower()
    if any(name_lower.startswith(p) for p in BOOL_FIELD_PREFIXES):
        return True
    if any(name_lower.endswith(s) for s in BOOL_FIELD_SUFFIXES):
        return True
    return False


def _has_dataclass_decorator(decorators: list[ast.AST]) -> bool:
    for d in decorators:
        # @dataclass
        if isinstance(d, ast.Name) and d.id == "dataclass":
            return True
        # @dataclass(...) 或 @dataclasses.dataclass(...)
        if isinstance(d, ast.Call):
            f = d.func
            if isinstance(f, ast.Name) and f.id == "dataclass":
                return True
            if isinstance(f, ast.Attribute) and f.attr == "dataclass":
                return True
        if isinstance(d, ast.Attribute) and d.attr == "dataclass":
            return True
    return False


# ── 扫描器 ───────────────────────────────────────────────────────────────
class DebtScanner(ast.NodeVisitor):
    def __init__(self, file_path: str) -> None:
        self.file = file_path
        self.violations: list[DebtViolation] = []

    # --- Class 检测 DEBT-1 + DEBT-3 ---
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        is_dataclass = _has_dataclass_decorator(node.decorator_list)

        action_fields: list[tuple[str, int]] = []
        bool_flag_fields: list[tuple[str, int]] = []

        for stmt in node.body:
            if not isinstance(stmt, ast.AnnAssign):
                continue
            field_name = stmt.target.id if isinstance(stmt.target, ast.Name) else ""
            if not field_name:
                continue
            if _is_action_field(field_name, stmt.annotation):
                action_fields.append((field_name, stmt.lineno))
            if _is_bool_flag_field(field_name, stmt.annotation):
                bool_flag_fields.append((field_name, stmt.lineno))

        if action_fields and len(bool_flag_fields) >= MIN_REDUNDANT_BOOL_FIELDS:
            code = "DEBT-1" if is_dataclass else "DEBT-3"
            action_str = ",".join(n for n, _ in action_fields)
            bool_str = ",".join(n for n, _ in bool_flag_fields)
            self.violations.append(DebtViolation(
                code=code,
                file=self.file,
                line=node.lineno,
                symbol=node.name,
                detail=f"action 字段 [{action_str}] 与 {len(bool_flag_fields)} 个派生布尔字段 "
                      f"[{bool_str}] 共存 → 应改为 Enum + @property 派生（5.96.2 病根）",
            ))

        self.generic_visit(node)

    # --- 函数检测 DEBT-2 ---
    def _check_function_args(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        args = node.args
        # R68 修订：只检测位置参数（posonly + positional），不检测 kwonlyargs
        # 原因：keyword-only 参数已用 `*` 隔离，调用方必须写 `name=value`，不会传错顺序
        # 5.96.3 病根是 _calculate_trust(git_ok, test_ok, audit_ok) 三位置参数，
        # 调用方写 _calculate_trust(True, True, False) 时无法区分哪个是 git 哪个是 test
        all_args = list(args.posonlyargs) + list(args.args)
        # 排除 self/cls
        if all_args and all_args[0].arg in ("self", "cls"):
            all_args = all_args[1:]

        bool_params: list[str] = []
        for arg in all_args:
            if _is_bool_annotation(arg.annotation):
                bool_params.append(arg.arg)

        if len(bool_params) >= MAX_BOOL_PARAMS:
            self.violations.append(DebtViolation(
                code="DEBT-2",
                file=self.file,
                line=node.lineno,
                symbol=node.name,
                detail=f"含 {len(bool_params)} 个 bool 位置参数 [{','.join(bool_params)}] "
                      f"→ 应改为 dict[str, bool] 或 keyword-only（5.96.3 病根；注：keyword-only bool 不算蔓延）",
            ))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function_args(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function_args(node)
        self.generic_visit(node)


# ── 入口 ─────────────────────────────────────────────────────────────────
def scan_file(path: Path) -> list[DebtViolation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as e:
        # 语法错误让其他 gate 处理，本扫描器放过
        _ = e
        return []
    scanner = DebtScanner(str(path))
    scanner.visit(tree)
    return scanner.violations


def scan_dir(root: Path) -> Iterable[DebtViolation]:
    for py in root.rglob("*.py"):
        # 跳过 __pycache__ / 测试 / 临时文件
        if "__pycache__" in py.parts:
            continue
        if "tests" in py.parts:
            continue
        if py.name.startswith("_tmp_") or py.name.startswith("_debug_"):
            continue
        yield from scan_file(py)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="架构债务扫描器（5.96 维度防御）")
    parser.add_argument("--src", default="src/zephyr", help="扫描根目录")
    parser.add_argument("--ci", action="store_true", help="CI 模式：违规即 exit 1（hard block）")
    parser.add_argument("--quiet", action="store_true", help="仅打印违规数，不打印详情")
    args = parser.parse_args(argv)

    root = Path(args.src)
    if not root.exists():
        print(f"ERROR: 扫描根目录不存在: {root}", file=sys.stderr)
        return 2

    all_violations: list[DebtViolation] = list(scan_dir(root))

    # 按类别统计
    by_code: dict[str, int] = {}
    for v in all_violations:
        by_code[v.code] = by_code.get(v.code, 0) + 1

    if not args.quiet:
        for v in all_violations:
            print(v.format())
        print(
            f"\n扫描完成: {root} | 总违规 {len(all_violations)} 条 "
            f"(DEBT-1 dataclass布尔冗余={by_code.get('DEBT-1', 0)}, "
            f"DEBT-2 bool参数蔓延={by_code.get('DEBT-2', 0)}, "
            f"DEBT-3 class action+bool共存={by_code.get('DEBT-3', 0)})",
            file=sys.stderr,
        )
    else:
        print(f"总违规 {len(all_violations)} 条: {by_code}")

    if args.ci and all_violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
