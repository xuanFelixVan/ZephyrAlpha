# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_pit_compliance.py | §
# [MODULE] scripts.governance.d7_code.check_pit_compliance
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
"""check_pit_compliance.py — PIT 合规检查（HC-10）

对标：GOV-AI-009 HC-10（PIT 铁律绕过——回测代码访问了未来数据）

检测内容：
- 回测/因子计算代码中是否引用了未来数据（lookahead bias）
- 检测模式：shift(-N)、iloc[i+N]、未来日期引用、未使用 .shift(1) 的标签构造

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --module, type: str, description: "检查指定模块路径的 PIT 合规性"}
- {flag: --scan-all, action: store_true, description: "扫描所有回测/因子代码"}
description: >
  PIT 合规检查（HC-10）——回测代码访问未来数据检测。
  对标 GOV-AI-009 ai-hallucination-detection-rules.md。
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import ast
import re
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
SCAN_DIRS = ["factor", "signal", "risk"]  # noqa: gate-vocab  PIT 扫描目录业务子集

LOOKAHEAD_PATTERNS = [
    (re.compile(r"\.shift\s*\(\s*-\s*\d+"), "shift(-N) — negative shift accesses future data"),
    (re.compile(r"\.iloc\s*\[\s*\w+\s*\+\s*\d+"), "iloc[i+N] — forward index access"),
    (re.compile(r"\.loc\s*\[\s*\w+\s*\+\s*\d+"), "loc[i+N] — forward index access"),
    (re.compile(r"future_data|lookahead|look_ahead"), "explicit future/lookahead reference"),
    (re.compile(r"\.shift\s*\(\s*0\s*\)"), "shift(0) — no shift applied, potential lookahead"),
]

LABEL_WITHOUT_SHIFT = re.compile(r"^(label|target|y_\w+)$", re.IGNORECASE)
LABEL_WHITELIST = re.compile(
    r"^(target_weight|target_path|target_module|target_dir|target_symbol|target_id|target_name|target_type|target_port|target_host|target_url|target_file|target_config|target_key|target_code|target_value)$",
    re.IGNORECASE,
)


def check_file_pit(filepath: Path) -> list[str]:
    """Check compliance and report findings."""
    findings = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return findings

    rel = filepath.relative_to(REPO_ROOT)
    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        for pattern, desc in LOOKAHEAD_PATTERNS:
            if pattern.search(stripped):
                findings.append(f"HC-10 WARNING: {rel}:{i} — {desc}: {stripped[:80]}")
                break

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and LABEL_WITHOUT_SHIFT.match(target.id)
                and not LABEL_WHITELIST.match(target.id)
            ):
                assign_str = ast.dump(node.value)
                if "shift" not in assign_str and "diff" not in assign_str and "pct_change" not in assign_str:
                    findings.append(
                        f"HC-10 WARNING: {rel} — label variable '{target.id}' assigned without .shift(1) or equivalent lag"
                    )

    return findings


def scan_all_dirs() -> list[str]:
    """scan_all_dirs implementation."""
    findings = []
    for dir_name in SCAN_DIRS:
        scan_dir = SRC_ROOT / dir_name
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            findings.extend(check_file_pit(py_file))
    return findings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="PIT compliance check (HC-10)")
    parser.add_argument("--module", type=str, help="Check specific module path")
    parser.add_argument("--scan-all", action="store_true", help="Scan all backtest/factor code")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []

    if args.module:
        p = Path(args.module)
        if p.is_dir():
            for py_file in p.rglob("*.py"):
                all_findings.extend(check_file_pit(py_file))
        elif p.suffix == ".py":
            all_findings.extend(check_file_pit(p))

    if args.scan_all or not args.module:
        all_findings.extend(scan_all_dirs())

    for finding in all_findings:
        print(finding)

    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
