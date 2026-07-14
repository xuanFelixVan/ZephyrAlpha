# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_module_id.py | §
# [MODULE] scripts.governance.d3_metadata.validate_module_id
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
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
GATE-MODULEID: Validate module_id uniqueness and index/file consistency.
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args:
- {flag: --dim, type: int, description: "仅检查指定维度（1-4）"}
- {flag: --warn-only, type: bool, description: "发现冲突时仅警告不阻断"}
description: >
  GATE-MODULEID 门禁——四维 module_id 校验（唯一性 + index.md 表-文件一致性 +
  命名规范 DOMAIN-TYPE-NNN + 连续编号无意外缺口）。对标 §6.13 枚举同步 + §6.11 索引-实际同步。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.frontmatter import extract_module_id

POLICIES_ROOT = REPO_ROOT / "docs/01_policies_and_standards"
MODULE_ID_PATTERN = re.compile("^[A-Z]+(-[A-Z0-9]+)+$")


def scan_all_module_ids() -> dict[str, list[Path]]:
    """scan_all_module_ids implementation."""
    id_map: dict[str, list[Path]] = defaultdict(list)
    for f in POLICIES_ROOT.rglob("*"):
        if f.suffix not in (".md", ".yaml", ".yml"):
            continue
        mid = extract_module_id(f)
        if mid:
            id_map[mid].append(f)
    return id_map


def check_dim1(id_map: dict[str, list[Path]]) -> list[str]:
    """Check compliance and report findings."""
    errors = []
    for mid, paths in sorted(id_map.items()):
        if len(paths) > 1:
            rels = [str(p.relative_to(POLICIES_ROOT)) for p in paths]
            errors.append(f"DIM-1 FAIL: module_id '{mid}' assigned to {len(paths)} files: {rels}")
    return errors


def check_dim3(id_map: dict[str, list[Path]]) -> list[str]:
    """Check compliance and report findings."""
    errors = []
    for mid, paths in sorted(id_map.items()):
        if mid.startswith("DEPRECATED-"):
            continue
        if not MODULE_ID_PATTERN.match(mid):
            errors.append(
                f"DIM-3 FAIL: module_id '{mid}' in {paths[0].relative_to(POLICIES_ROOT)} does not match DOMAIN-TYPE-NNN format"
            )
    return errors


def check_dim4(id_map: dict[str, list[Path]]) -> list[str]:
    """Check compliance and report findings."""
    errors = []
    domain_nums: dict[str, list[int]] = defaultdict(list)
    for mid in id_map:
        if mid.startswith("DEPRECATED-"):
            continue
        m = re.match("^([A-Z]+-[A-Z]+)-(\\d{3})$", mid)
        if m:
            prefix = m.group(1)
            num = int(m.group(2))
            domain_nums[prefix].append(num)
    for prefix, nums in sorted(domain_nums.items()):
        nums.sort()
        for i in range(len(nums) - 1):
            if nums[i + 1] - nums[i] > 1:
                gap_start = nums[i] + 1
                gap_end = nums[i + 1] - 1
                if gap_start == gap_end:
                    errors.append(
                        f"DIM-4 WARN: {prefix} has gap at {prefix}-{gap_start:03d} (found {prefix}-{nums[i]:03d} then {prefix}-{nums[i + 1]:03d})"
                    )
    return errors


def check_dim2() -> list[str]:
    """Check compliance and report findings."""
    errors = []
    for idx_file in POLICIES_ROOT.rglob("index.md"):
        try:
            text = idx_file.read_text(encoding="utf-8")
        except Exception:
            continue
        table_rows = re.findall(
            "\\|\\s*`?([^\\s|`]+\\.md| [^\\s|`]+\\.yaml)`?\\s*\\|\\s*([A-Z]+-[A-Z]+-\\d{3})\\s*\\|", text
        )
        if not table_rows:
            table_rows = re.findall(
                "\\|\\s*\\[?[^\\]]*\\]?\\(?([^)|\\s]+\\.(?:md|yaml))\\)?\\s*\\|\\s*([A-Z]+-[A-Z]+-\\d{3})\\s*\\|", text
            )
        for ref_path_str, claimed_id in table_rows:
            ref_path = idx_file.parent / ref_path_str
            if not ref_path.exists():
                continue
            actual_id = extract_module_id(ref_path)
            if actual_id and actual_id != claimed_id:
                rel_idx = str(idx_file.relative_to(POLICIES_ROOT))
                rel_ref = str(ref_path.relative_to(POLICIES_ROOT))
                errors.append(
                    f"DIM-2 FAIL: {rel_idx} claims {ref_path_str}={claimed_id}, but file has module_id={actual_id}"
                )
    return errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="GATE-MODULEID: Validate module_id uniqueness and consistency")
    parser.add_argument("--dim", type=int, choices=[1, 2, 3, 4], help="Check only this dimension")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    print("GATE-MODULEID: Scanning module_id assignments...")
    id_map = scan_all_module_ids()
    print(f"  Found {len(id_map)} unique module_ids across {sum(len(v) for v in id_map.values())} files")
    all_errors = []
    all_warnings = []
    if not args.dim or args.dim == 1:
        errs = check_dim1(id_map)
        all_errors.extend(errs)
        print(f"  DIM-1 (uniqueness): {('PASS' if not errs else f'{len(errs)} errors')}")
    if not args.dim or args.dim == 3:
        errs = check_dim3(id_map)
        all_errors.extend(errs)
        print(f"  DIM-3 (naming convention): {('PASS' if not errs else f'{len(errs)} errors')}")
    if not args.dim or args.dim == 4:
        errs = check_dim4(id_map)
        all_warnings.extend(errs)
        print(f"  DIM-4 (sequential coverage): {('PASS' if not errs else f'{len(errs)} warnings')}")
    if not args.dim or args.dim == 2:
        errs = check_dim2()
        all_errors.extend(errs)
        print(f"  DIM-2 (index-file consistency): {('PASS' if not errs else f'{len(errs)} errors')}")
    if all_warnings:
        print(f"\nGATE-MODULEID: {len(all_warnings)} warnings (non-blocking):")
        for w in all_warnings:
            print(f"  {w}")
    if all_errors:
        print(f"\nGATE-MODULEID: FAIL — {len(all_errors)} errors found")
        for e in all_errors:
            print(f"  {e}")
        return EXIT_FINDINGS
    print("\nGATE-MODULEID: ALL PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
