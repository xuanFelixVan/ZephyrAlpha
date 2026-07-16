# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_idempotency.py | §
# [MODULE] scripts.governance.d7_code.check_idempotency
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
"""check_idempotency.py — 幂等性缺失检查（HC-9）

对标：GOV-AI-009 HC-9（幂等性缺失——D_EXECUTION_CORE 执行层代码缺少幂等 Key）

检测内容：
- D_EXECUTION_CORE 执行层模块的公共方法是否声明了幂等 Key（idempotency_key 参数或装饰器）
- 检查 @idempotent 装饰器或 idempotency_key 参数的存在性

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --module, type: str, description: "检查指定模块路径的幂等性"}
- {flag: --scan-all, action: store_true, description: "扫描所有 D_EXECUTION_CORE 执行层代码"}
description: >
  幂等性缺失检查（HC-9）——D_EXECUTION_CORE 执行层代码缺少幂等 Key 检测。
  对标 GOV-AI-009 ai-hallucination-detection-rules.md。
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: true
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
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

SRC_ROOT = REPO_ROOT / "src" / "zephyr"
L06_DIRS = ["ex_core"]

IDEMPOTENCY_MARKERS = ["idempotency_key", "idempotent", "idempotency", "Idempotency-Key"]


def check_file_idempotency(filepath: Path) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        has_idempotency = False
        for deco in node.decorator_list:
            deco_str = ast.dump(deco)
            for marker in IDEMPOTENCY_MARKERS:
                if marker in deco_str:
                    has_idempotency = True
                    break
        for arg in node.args.args:
            if any(marker in arg.arg for marker in IDEMPOTENCY_MARKERS):
                has_idempotency = True
                break
        if not has_idempotency:
            docstring = ast.get_docstring(node) or ""
            if any(marker in docstring for marker in IDEMPOTENCY_MARKERS):
                has_idempotency = True
        if not has_idempotency:
            rel = filepath.relative_to(REPO_ROOT)
            findings.append(f"HC-9 WARNING: {rel}::{node.name}() — D_EXECUTION_CORE execution layer method missing idempotency_key")
    return findings


def scan_ex_core() -> list[str]:
    """scan_ex_core implementation."""
    findings = []
    for ex_core in L06_DIRS:
        ex_core = SRC_ROOT / ex_core
        if not ex_core.exists():
            continue
        for py_file in ex_core.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            findings.extend(check_file_idempotency(py_file))
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Idempotency check (HC-9)")
    parser.add_argument("--module", type=str, help="Check specific module path")
    parser.add_argument("--scan-all", action="store_true", help="Scan all D_EXECUTION_CORE execution layer code")
    parser.add_argument("--warn-only", action="store_true", default=True, help="Only warn (default)")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.module:
        p = Path(args.module)
        if p.is_dir():
            for py_file in p.rglob("*.py"):
                all_findings.extend(check_file_idempotency(py_file))
        elif p.suffix == ".py":
            all_findings.extend(check_file_idempotency(p))

    if args.scan_all:
        all_findings.extend(scan_ex_core())

    if not any([args.module, args.scan_all]):
        all_findings.extend(scan_ex_core())

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
