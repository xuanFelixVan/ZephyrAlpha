#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_SCRIPTS-001 | scripts/governance/d7_code/scan_complexity.py | §
# [MODULE] scripts.governance.d7_code.scan_complexity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(ast/pathlib/dataclasses/argparse/statistics)
# [CONSUMERS] CI/CD reporting; manual audit; architecture_debt_registry §5.158 暗债监控
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 实现；非阻断（exit 0 除非 --ci）；McCabe 算法与 high_complexity_gate.py 一致
# [MODIFY-GUARD] 修改阈值需同步更新 architecture_debt_registry §5.158 + high_complexity_gate.py _MAX_COMPLEXITY
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=clean/warn-only / 1=--ci 且有违规 / 2=src dir missing
# [TESTS] 手动验证: 裁定#214 基线 215 暗债函数(复杂度>15), 最高105, 平均3.4
# [TTL] permanent
"""
全量循环复杂度扫描器 — §5.158 暗债监控（裁定#214 Phase 4 引入）。

NO-HIGH-COMPLEXITY gate (priority=85) 只检测**新增**函数的复杂度（裁定#214 修复后），
存量高复杂度函数（暗债）不在 gate 覆盖范围。本扫描器补位——全量扫描 src/zephyr/
所有 .py 文件，报告复杂度 > 阈值（默认 15）的函数，让暗债可见。

病根对标：
  - §5.158 第93轮声明"全部清零"但 11 个高复杂度函数从未登记（暗债盲区）
  - 裁定#214 治本：gate fix（Phase 1）+ 暗债登记（Phase 2）+ 全量扫描（Phase 4）
  - 本脚本 = Phase 4：持续监控防线，防止未来产生新的暗债

设计原则（对标 check_any_abuse.py / scan_debt.py）：
  - 纯 stdlib（ast + pathlib），不依赖 ruff/mypy/radon 是否安装
  - 非阻断：默认 exit 0（CI/CD 报告用）；--ci 模式 exit 1 有违规时
  - McCabe 算法与 high_complexity_gate.py._cyclomatic_complexity 完全一致
  - tests/ 豁免（与 gate 一致）

使用：
  python scripts/governance/d7_code/scan_complexity.py [--src DIR] [--ci] [--quiet] [--threshold N]

退出码：
  0 = clean / warn-only 模式下有违规也返回 0
  1 = --ci 模式下检测到违规（CI/CD 阻断）
  2 = src 目录缺失或参数错误
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

# ── 阈值（与 high_complexity_gate.py _MAX_COMPLEXITY 一致）─────────────
_MAX_COMPLEXITY = 15


@dataclass
class ComplexityFinding:
    """单条高复杂度函数记录。"""

    file: str
    line: int
    function: str
    complexity: int
    end_line: int = 0

    def format(self) -> str:
        """格式化为可读字符串。"""
        suffix = f"-{self.end_line}" if self.end_line else ""
        return (
            f"{self.file}:{self.line}{suffix}: "
            f"{self.function}(complexity={self.complexity})"
        )


def _cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """计算函数的循环复杂度（McCabe）。

    与 high_complexity_gate.py._cyclomatic_complexity 算法完全一致：
    基础复杂度=1，每个决策点+1：
    - If / IfExp
    - For / AsyncFor / While
    - ExceptHandler
    - BoolOp(And/Or) 每个操作数（len(values)-1）
    - comprehension 的 if 子句
    """
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            complexity += len(child.ifs)
    return complexity


def _is_test_file(filepath: str) -> bool:
    """判断是否是测试文件（tests/ 目录或 test_*.py / *_test.py）。"""
    fp = filepath.replace("\\", "/")
    if "/tests/" in fp or fp.startswith("tests/"):
        return True
    basename = Path(fp).name
    return basename.startswith("test_") or basename.endswith("_test.py")


def _scan_file(filepath: Path, threshold: int) -> list[ComplexityFinding]:
    """扫描单个文件，返回复杂度 > threshold 的函数列表。"""
    findings: list[ComplexityFinding] = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return findings

    rel_path = str(filepath).replace("\\", "/")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = _cyclomatic_complexity(node)
            if complexity > threshold:
                findings.append(ComplexityFinding(
                    file=rel_path,
                    line=node.lineno,
                    function=node.name,
                    complexity=complexity,
                    end_line=getattr(node, "end_lineno", node.lineno),
                ))
    return findings


def scan_directory(
    src_dir: Path, threshold: int
) -> tuple[list[ComplexityFinding], int, list[int]]:
    """扫描目录下所有 .py 文件（排除 tests/）。

    Returns:
        (findings, total_functions, all_complexities)
    """
    findings: list[ComplexityFinding] = []
    total_functions = 0
    all_complexities: list[int] = []

    for py_file in sorted(src_dir.rglob("*.py")):
        rel = str(py_file).replace("\\", "/")
        if _is_test_file(rel):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_functions += 1
                c = _cyclomatic_complexity(node)
                all_complexities.append(c)
                if c > threshold:
                    findings.append(ComplexityFinding(
                        file=rel,
                        line=node.lineno,
                        function=node.name,
                        complexity=c,
                        end_line=getattr(node, "end_lineno", node.lineno),
                    ))
    return findings, total_functions, all_complexities


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="全量循环复杂度扫描器 — §5.158 暗债监控（裁定#214 Phase 4）"
    )
    parser.add_argument(
        "--src", default="src/zephyr",
        help="源码目录（默认: src/zephyr）",
    )
    parser.add_argument(
        "--threshold", type=int, default=_MAX_COMPLEXITY,
        help=f"复杂度阈值（默认: {_MAX_COMPLEXITY}，与 gate 一致）",
    )
    parser.add_argument(
        "--ci", action="store_true",
        help="CI 模式：有违规时 exit 1（默认 warn-only exit 0）",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="静默模式：只输出违规列表，不输出统计摘要",
    )
    args = parser.parse_args(argv)

    src_dir = Path(args.src)
    if not src_dir.is_dir():
        print(f"[scan_complexity] 错误: src 目录不存在: {src_dir}", file=sys.stderr)
        return 2

    findings, total_functions, all_complexities = scan_directory(
        src_dir, args.threshold
    )

    # 按复杂度降序排列
    findings.sort(key=lambda f: f.complexity, reverse=True)

    if findings:
        print(f"[scan_complexity] 发现 {len(findings)} 个高复杂度函数"
              f" (complexity > {args.threshold})：")
        for f in findings:
            print(f"  {f.format()}")
    else:
        if not args.quiet:
            print(f"[scan_complexity] 无高复杂度函数 (complexity > {args.threshold})")

    if not args.quiet:
        avg = mean(all_complexities) if all_complexities else 0.0
        max_c = max(all_complexities) if all_complexities else 0
        print(f"\n[scan_complexity] 统计摘要:")
        print(f"  扫描目录: {src_dir}")
        print(f"  总函数数: {total_functions}")
        print(f"  平均复杂度: {avg:.1f}")
        print(f"  最高复杂度: {max_c}")
        print(f"  超阈值函数: {len(findings)} (阈值={args.threshold})")

    if args.ci and findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
