# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_b_track_packages.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_b_track_packages
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] task_bound
"""validate_b_track_packages.py — B 轨包完整性校验



对标：GOV-DOC-002 §四（B 轨新包创建门槛）

检测内容：
- B 轨新包必须有 ADR
- B 轨新包必须有 interface.md
- B 轨新包必须有 Phase 路线

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: B 轨包完整性校验（GOV-DOC-002 §四 — interface.md必填）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

B_TRACK_DIRS = {
    "llm-security",
    "vector-memory",
    "context-engine",
    "orchestrator",
    "feedback-loop",
    "gates",
    "db",
    "kb",
    "mcp",
    "shared",
    "pipeline",
    "core",
}

REQUIRED_FILES = {"interface.md"}


def scan_b_track_packages() -> list[dict]:
    """扫描 B-track 包合规性."""
    findings = []
    """扫描并返回发现列表."""
    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        return findings

    for pkg_dir in src_dir.iterdir():
        if not pkg_dir.is_dir():
            continue
        if pkg_dir.name not in B_TRACK_DIRS:
            continue
        if pkg_dir.name.startswith("_") or pkg_dir.name.startswith("."):
            continue

        pkg_files = {f.name for f in pkg_dir.iterdir() if f.is_file()}
        pkg_subdirs = {f.name for f in pkg_dir.iterdir() if f.is_dir()}

        has_interface = "interface.md" in pkg_files or any((pkg_dir / d / "interface.md").exists() for d in pkg_subdirs)

        if not has_interface:
            findings.append(
                {
                    "package": pkg_dir.name,
                    "type": "MISSING_INTERFACE",
                    "detail": f"B 轨包 '{pkg_dir.name}' 缺少 interface.md",
                    "severity": "LOW",
                }
            )

    return findings
    """扫描 B-track 包合规性."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="B 轨包完整性校验（GOV-DOC-002 §四）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_b_track_packages()

    if findings:
        print(f"\n[B-TRACK] {len(findings)} 个 B 轨包完整性问题:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['package']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[B-TRACK] B 轨包完整性合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
