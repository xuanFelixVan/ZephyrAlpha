# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_orphan_outputs.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_orphan_outputs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_orphan_outputs
[INVARIANTS] 扫描蓝图 §11 产出物 consumer_min; 检测零消费者孤儿产出物
[MODIFY-GUARD] script_manifest.yaml; blueprint-construction-template.md
[CONSUMERS] CI pipeline; AI session 冷启动
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=ORPHANS, exit 2=ERROR
[TESTS] tests/governance/test_check_orphan_outputs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re
import subprocess

from _shared.constants import BLUEPRINTS_DIR, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files

__manifest__ = """
args: [--warn-only]
description: 蓝图产出物孤儿检测——检测蓝图中零消费者的产出物
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

SRC_DIR = REPO_ROOT / "src" / "zephyr"


def count_importers(module_path: str) -> int:
    parts = module_path.rstrip("/").split("/")
    if len(parts) >= 2:
        import_stmt = f"from zephyr.{'.'.join(parts[-2:])}"
    else:
        import_stmt = f"from zephyr.{parts[-1]}"
    try:
        result = subprocess.run(["rg", "-c", import_stmt, str(SRC_DIR)], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return 0
        return len([line for line in result.stdout.strip().splitlines() if line])
    except Exception:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check orphan outputs across blueprints")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even if orphans found")
    args = parser.parse_args()

    if not BLUEPRINTS_DIR.exists():
        print("ERROR: blueprints directory not found")
        return EXIT_ERROR

    orphans = []
    for bp in iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md"):
        content = bp.read_text(encoding="utf-8")
        module_id = bp.parent.name
        in_section11 = False
        for line in content.splitlines():
            if "§11" in line or "产出物" in line:
                in_section11 = True
                continue
            if in_section11 and line.startswith("##"):
                break
            if in_section11 and "|" in line and "src/zephyr" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    path_part = parts[2] if len(parts) > 2 else ""
                    consumer_min_str = parts[4] if len(parts) > 4 else "≥1"
                    if "src/zephyr" in path_part:
                        match = re.search(r"src/zephyr/([^\s`|]+)", path_part)
                        if match:
                            module_path = match.group(1).rstrip("/`")
                            min_val = 1
                            m = re.search(r"≥(\d+)", consumer_min_str)
                            if m:
                                min_val = int(m.group(1))
                            if min_val > 0:
                                actual = count_importers(module_path)
                                if actual < min_val:
                                    orphans.append((module_id, module_path, min_val, actual))

    if orphans:
        print(f"ORPHAN OUTPUTS: {len(orphans)}")
        print(f"{'蓝图':<25} {'产出物路径':<50} {'要求':>6} {'实际':>6}")
        print("-" * 90)
        for mid, path, req, actual in orphans:
            print(f"{mid:<25} {path:<50} ≥{req:>4} {actual:>4}")
        if args.warn_only:
            print("WARN: orphans found but --warn-only mode")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("ORPHAN CHECK: CLEAN — no orphan outputs found")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
