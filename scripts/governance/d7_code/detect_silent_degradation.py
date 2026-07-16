# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_silent_degradation.py | §
# [MODULE] scripts.governance.d7_code.detect_silent_degradation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
"""
detect_silent_degradation.py — 静默降级检测



对标：COND-45（服务降级不写入日志为条件禁止）

检测内容：
- 扫描降级代码路径（fallback/default/except 块）
- 检查是否有日志写入调用
- 降级路径无日志 = 运维盲区

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 静默降级检测（COND-45 — 降级路径必须有日志）
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: false
"""


import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

DEGRADATION_KEYWORDS = {"fallback", "default", "degraded", "degradation", "circuit_breaker", "retry"}


def has_logging(stmts: list) -> bool:
    """判断函数是否包含日志记录"""
    for stmt in stmts:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if isinstance(func, ast.Name) and func.id in ("print", "logging", "logger"):
                return True
            if isinstance(func, ast.Attribute) and func.attr in (
                "error",
                "warning",
                "info",
                "debug",
                "critical",
                "warn",
                "log",
            ):
                return True
        if isinstance(stmt, ast.With):
            if has_logging(stmt.body):
                return True
        if isinstance(stmt, ast.If):
            if has_logging(stmt.body) or has_logging(stmt.orelse):
                return True
    return False
    "判断函数是否包含日志记录."


def check_silent_degradation(filepath: Path) -> list[dict]:
    """检查静默降级"""
    findings = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings
    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if not node.body:
                continue
            is_degradation = False
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and any(k in target.id.lower() for k in DEGRADATION_KEYWORDS):
                            is_degradation = True
                if isinstance(stmt, ast.Return):
                    if isinstance(stmt.value, ast.Name) and any(
                        k in stmt.value.id.lower() for k in DEGRADATION_KEYWORDS
                    ):
                        is_degradation = True
            if is_degradation and (not has_logging(node.body)):
                findings.append({"file": rel, "line": node.lineno, "severity": "MEDIUM"})
    return findings
    "检查静默降级."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="静默降级检测（COND-45）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[SILENT-DEGRADATION] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_silent_degradation(filepath)
        all_findings.extend(findings)
    if all_findings:
        print(f"\n[SILENT-DEGRADATION] {len(all_findings)} 个静默降级:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print("    降级路径无日志写入", file=sys.stderr)
    else:
        print("[SILENT-DEGRADATION] 无静默降级", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
