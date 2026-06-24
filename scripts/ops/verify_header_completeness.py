# [BLUEPRINT] MOD-INF-005 | scripts/ops/verify_header_completeness.py | §
# [MODULE] scripts.ops.verify_header_completeness
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.ops.fill_blueprint_ids
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
import re
from collections import defaultdict
from pathlib import Path

SRC_ROOT = Path(r"d:\ZephyrAlpha\src\zephyr")

REQUIRED_FIELDS = [
    "BLUEPRINT", "MODULE", "DOMAIN", "DEPENDENCIES",
    "CONSUMERS", "STARTUP", "MATURITY",
    "INVARIANTS", "MODIFY-GUARD",
    "STABILITY", "SAFETY", "AI_AUTONOMY",
]
OPTIONAL_FIELDS = ["ERROR_CONTRACT", "TESTS"]
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

HEADER_PATTERN = re.compile(r"^#\s*\[(\w[\w-]*)\]")

files_scanned = 0
files_complete = 0
files_missing_req = 0
missing_stats = defaultdict(int)
missing_files = defaultdict(list)


def scan_file(filepath: Path):
    global files_scanned
    files_scanned += 1

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    found_fields = set()
    for line in lines[:30]:
        m = HEADER_PATTERN.match(line.rstrip("\n"))
        if m:
            found_fields.add(m.group(1))

    missing_req = [f for f in REQUIRED_FIELDS if f not in found_fields]
    missing_opt = [f for f in OPTIONAL_FIELDS if f not in found_fields]

    if not missing_req:
        global files_complete
        files_complete += 1
    else:
        global files_missing_req
        files_missing_req += 1
        for f in missing_req:
            missing_stats[f] += 1
            missing_files[f].append(str(filepath.relative_to(SRC_ROOT)))

    for f in missing_opt:
        missing_stats[f] += 1


def main():
    py_files = sorted(SRC_ROOT.rglob("*.py"))

    for fp in py_files:
        if fp.name == "__init__.py":
            continue
        scan_file(fp)

    print("=" * 70)
    print("HEADER FOURTEEN-FIELD COMPLETENESS VERIFICATION")
    print("=" * 70)
    print(f"Files scanned:           {files_scanned}")
    print(f"Files complete (all req): {files_complete}")
    print(f"Files missing required:   {files_missing_req}")
    print()
    print("MISSING FIELD STATISTICS:")
    print(f"  {'Field':<20} {'Missing':>8} {'Type':>6}")
    print(f"  {'-' * 20} {'-' * 8} {'-' * 6}")
    for f in ALL_FIELDS:
        req_tag = "REQ" if f in REQUIRED_FIELDS else "opt"
        print(f"  {f:<20} {missing_stats.get(f, 0):>8} {req_tag:>6}")

    if files_missing_req > 0:
        print("\nFiles missing required fields:")
        for f in REQUIRED_FIELDS:
            if missing_files[f]:
                print(f"\n  [{f}] missing in {len(missing_files[f])} files:")
                for fn in missing_files[f][:5]:
                    print(f"    - {fn}")
                if len(missing_files[f]) > 5:
                    print(f"    ... and {len(missing_files[f]) - 5} more")

    print("\n" + "=" * 70)
    if files_missing_req == 0:
        print("RESULT: ALL FILES HAVE COMPLETE REQUIRED HEADERS ✓")
    else:
        print(f"RESULT: {files_missing_req} FILES STILL MISSING REQUIRED FIELDS ✗")
    print("=" * 70)


if __name__ == "__main__":
    main()
