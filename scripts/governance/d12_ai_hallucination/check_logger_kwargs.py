# [BLUEPRINT] MOD-INF-005 | scripts/governance/d12_ai_hallucination/check_logger_kwargs.py | §
# [MODULE] scripts.governance.d12_ai_hallucination.check_logger_kwargs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d12_ai_hallucination.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""========================================================

病根（Root Cause）：项目存在双日志系统（structlog + 标准 logging），
但缺乏自动化检测手段。开发者可能将 structlog 风格的 key=value 关键字参数
误用于标准 logging.Logger 调用，导致运行时 TypeError。

检查逻辑：
  1. 扫描 src/zephyr/ 下所有 .py 文件
  2. 查找所有 logger.info/warning/error/debug/exception 调用
  3. 标记使用了非标准关键字参数的调用
  4. 标准关键字参数：exc_info, extra, stack_info, stacklevel — 这些是合法的
  5. 其余所有 key=value 形式的关键字参数均视为 structlog-style 混用

防护层级：
  --ci          硬阻断模式（exit 1 = 拒绝提交），pre_commit / CI 中启用
  (默认)        报告模式（exit 0 但打印违规，用于手动审计）

注册位置：11_d12_ai_hallucination 线下 — 对标 IRN-011 ZR-007 (自净检测)
            GATE-SLOG: .pre_commit-config.yaml + CI governance.yml
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
dimensions: [D12]
priority: P1
timeout_seconds: 30
args:
  - {flag: --ci, type: bool, description: "硬阻断模式（exit 1）"}
  - {flag: --warn-only, type: bool, description: "仅警告模式"}
warn_only: false
description: 日志完整性检查——检测 structlog-style 关键字参数混用标准 logging
"""

import argparse
import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

PROJECT_ROOT = REPO_ROOT
SCAN_ROOT = PROJECT_ROOT / "src" / "zephyr"
STDLIB_LOGGER_KWARGS = frozenset({"exc_info", "extra", "stack_info", "stacklevel"})


def _is_suspicious_call(call_node: ast.Call) -> bool:
    """_is_suspicious_call implementation."""
    kwargs = {kw.arg: kw.value for kw in call_node.keywords if kw.arg is not None}
    suspicious = {k for k in kwargs if k not in STDLIB_LOGGER_KWARGS}
    return bool(suspicious)


def _find_logger_calls(tree: ast.AST) -> list[tuple[int, str]]:
    """_find_logger_calls implementation."""
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        match node.func:
            case ast.Attribute(value=ast.Name(), attr=method) if method in {
                "debug",
                "info",
                "warning",
                "error",
                "exception",
            }:
                if _is_suspicious_call(node):
                    bad_kwargs = [
                        kw.arg for kw in node.keywords if kw.arg is not None and kw.arg not in STDLIB_LOGGER_KWARGS
                    ]
                    findings.append((node.lineno, f"{method}(msg, ..., {', '.join(bad_kwargs)})"))
    return findings


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="检查 structlog-style logger 混用")
    parser.add_argument("--ci", action="store_true", help="硬阻断模式：有违规→exit 1")
    args = parser.parse_args()

    total = 0
    files_with_issues: list[tuple[Path, list[tuple[int, str]]]] = []

    for py_file in SCAN_ROOT.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        findings = _find_logger_calls(tree)
        if findings:
            files_with_issues.append((py_file, findings))
            total += len(findings)

    if total == 0:
        print("[PASS] 零 structlog-style logger 关键字参数混用")
        return EXIT_PASS
    print(f"[FAIL] 发现 {total} 处 structlog-style logger 混用：")
    for path, issues in files_with_issues:
        rel = path.relative_to(PROJECT_ROOT)
        print(f"\n  {rel}:")
        for lineno, detail in issues:
            print(f"    L{lineno}: {detail}")

    print('\n  修复方法：将 logger.info("msg", foo=bar) 改为')
    print('            logger.info("msg: foo=%s", bar)')

    if args.ci:
        print("\n  GATE-SLOG HARD BLOCK: 拒绝提交。请修复上述违规后重试。")
        return EXIT_FINDINGS
    print("\n  [WARN] 在 --ci 模式下上述问题会导致提交被拒绝。")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
