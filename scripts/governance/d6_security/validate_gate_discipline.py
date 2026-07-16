# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/validate_gate_discipline.py | §
# [MODULE] scripts.governance.d6_security.validate_gate_discipline
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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
validate_gate_discipline.py — 门禁纪律校验



对标：COND-33~37（门禁级别动态升降/跳级/生产关闭门禁/AI自签豁免/Pydantic静默吞错）

检测内容：
- 代码中 enable_gate=False 在非测试环境使用
- Pydantic try/except 静默吞错模式
- 门禁绕过模式

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 门禁纪律校验（COND-33~37 — enable_gate=False+Pydantic静默吞错）
dimensions:
- D6
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
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse


def check_gate_bypass(filepath: Path) -> list[dict]:
    """检查门禁绕过"""
    findings = []
    "检查门禁绕过."
    try:
        "检查并返回违规列表."
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings
    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    is_test = "test" in rel.lower()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in ("enable_gate", "gate_enabled", "skip_gate", "bypass_gate"):
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        if not is_test:
                            findings.append(
                                {
                                    "file": rel,
                                    "line": node.lineno,
                                    "type": "GATE_DISABLED",
                                    "detail": f"非测试环境中 {kw.arg}=False",
                                    "severity": "HIGH",
                                }
                            )
    return findings
    "检查门禁绕过."


def check_pydantic_silence(filepath: Path) -> list[dict]:
    """检查 Pydantic 静默."""
    findings = []
    "检查并返回违规列表."
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    if "ValidationError" not in source and "BaseModel" not in source:
        return findings
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return findings
    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type and isinstance(node.type, ast.Name) and (node.type.id == "ValidationError"):
                if node.body:
                    is_silent = True
                    for stmt in node.body:
                        if isinstance(stmt, ast.Raise):
                            is_silent = False
                            break
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            func = stmt.value.func
                            if isinstance(func, ast.Name) and func.id in ("print", "logging", "logger"):
                                is_silent = False
                                break
                            if isinstance(func, ast.Attribute) and func.attr in (
                                "error",
                                "warning",
                                "info",
                                "debug",
                                "critical",
                            ):
                                is_silent = False
                                break
                    if is_silent:
                        findings.append(
                            {
                                "file": rel,
                                "line": node.lineno,
                                "type": "PYDANTIC_SILENT",
                                "detail": "ValidationError 被静默吞没（无 raise/log）",
                                "severity": "MEDIUM",
                            }
                        )
    return findings
    "检查 Pydantic 静默."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="门禁纪律校验（COND-33~37）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[GATE-DISCIPLINE] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    all_findings = []
    for filepath in iter_files(src_dir, extensions=frozenset({".py"})):
        all_findings.extend(check_gate_bypass(filepath))
        all_findings.extend(check_pydantic_silence(filepath))
    if all_findings:
        print(f"\n[GATE-DISCIPLINE] {len(all_findings)} 个门禁纪律违规:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[GATE-DISCIPLINE] 门禁纪律合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
