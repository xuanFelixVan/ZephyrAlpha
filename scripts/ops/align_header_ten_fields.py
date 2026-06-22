# [BLUEPRINT] MOD-INF-005 | scripts/ops/align_header_ten_fields.py | §
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SRC_ROOT = Path(r"d:\ZephyrAlpha\src\zephyr")

REQUIRED_FIELDS = {
    "BLUEPRINT": None,
    "MODULE": None,
    "INVARIANTS": "none",
    "MODIFY-GUARD": "none",
    "STABILITY": "evolving",
    "SAFETY": "L",
    "AI_AUTONOMY": "ai_modifiable",
}

OPTIONAL_FIELDS = {
    "CONSUMERS": None,
    "ERROR_CONTRACT": None,
    "TESTS": None,
}

ALL_FIELDS_ORDER = [
    "BLUEPRINT",
    "MODULE",
    "INVARIANTS",
    "MODIFY-GUARD",
    "CONSUMERS",
    "STABILITY",
    "SAFETY",
    "AI_AUTONOMY",
    "ERROR_CONTRACT",
    "TESTS",
]

HEADER_PATTERN = re.compile(r"^#\s*\[(\w+)\]\s*(.*)")

missing_stats = defaultdict(int)
fixed_stats = defaultdict(int)
files_scanned = 0
files_fixed = 0
files_complete = 0
files_skipped_init = 0


def scan_file(filepath: Path):
    global files_scanned
    files_scanned += 1

    rel = filepath.relative_to(SRC_ROOT.parent.parent)
    module_path = "zephyr." + ".".join(filepath.relative_to(SRC_ROOT).with_suffix("").parts)

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    header_lines = []
    header_end_idx = 0
    found_fields = {}

    for i, line in enumerate(lines[:15]):
        m = HEADER_PATTERN.match(line.rstrip("\n"))
        if m:
            field_name = m.group(1)
            found_fields[field_name] = m.group(2).strip()
            header_end_idx = i
            header_lines.append((i, field_name, line.rstrip("\n")))

    missing_required = [f for f in REQUIRED_FIELDS if f not in found_fields]
    missing_optional = [f for f in OPTIONAL_FIELDS if f not in found_fields]

    for f in missing_required:
        missing_stats[f] += 1
    for f in missing_optional:
        missing_stats[f] += 1

    if not missing_required:
        files_complete += 1
        return

    insert_lines = []
    for field_name in ALL_FIELDS_ORDER:
        if field_name in found_fields:
            continue
        if field_name in missing_required:
            default = REQUIRED_FIELDS[field_name]
            if field_name == "MODULE":
                default = module_path
            elif field_name == "BLUEPRINT":
                default = f"unknown | {rel} | §"
            if default is None:
                insert_lines.append(f"# [{field_name}]")
            else:
                insert_lines.append(f"# [{field_name}] {default}")
        elif field_name in missing_optional:
            insert_lines.append(f"# [{field_name}]")

    if not insert_lines:
        return

    new_lines = list(lines)

    if header_lines:
        last_header_line_idx = header_lines[-1][0]
        insert_pos = last_header_line_idx + 1
        while insert_pos < len(new_lines) and new_lines[insert_pos].strip() == "":
            insert_pos += 1
        block = "\n\n".join(insert_lines) + "\n\n"
        new_lines.insert(insert_pos, block)
    else:
        block = "\n\n".join(insert_lines) + "\n\n"
        new_lines.insert(0, block)

    content = "".join(new_lines)

    tmp_path = str(filepath) + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(filepath))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        print(f"  ERROR: Permission denied writing {filepath}", file=sys.stderr)
        return

    global files_fixed
    files_fixed += 1
    for f in missing_required:
        fixed_stats[f] += 1

    print(f"  FIXED: {filepath.relative_to(SRC_ROOT)} — added: {', '.join(missing_required)}")


def main():
    dry_run = "--dry-run" in sys.argv

    py_files = sorted(SRC_ROOT.rglob("*.py"))

    for fp in py_files:
        if fp.name == "__init__.py":
            global files_skipped_init
            files_skipped_init += 1
            continue
        scan_file(fp)

    print("\n" + "=" * 70)
    print("HEADER TEN-FIELD COMPLETENESS REPORT")
    print("=" * 70)
    print(f"Files scanned:    {files_scanned}")
    print(f"Files skipped (__init__.py): {files_skipped_init}")
    print(f"Files already complete:      {files_complete}")
    print(f"Files fixed:                 {files_fixed}")
    print()
    print("MISSING FIELD STATISTICS (required + optional):")
    print(f"  {'Field':<20} {'Missing':>8} {'Fixed':>8}")
    print(f"  {'-' * 20} {'-' * 8} {'-' * 8}")
    for f in ALL_FIELDS_ORDER:
        req_tag = " (REQ)" if f in REQUIRED_FIELDS else " (opt)"
        print(f"  {f + req_tag:<20} {missing_stats.get(f, 0):>8} {fixed_stats.get(f, 0):>8}")
    print()
    if files_fixed > 0:
        print("Defaults applied for missing required fields:")
        print("  [STABILITY]     evolving")
        print("  [SAFETY]        L")
        print("  [AI_AUTONOMY]   ai_modifiable")
        print("  [INVARIANTS]    none")
        print("  [MODIFY-GUARD]  none")
        print("  [MODULE]        auto-derived from file path")
        print("  [BLUEPRINT]     auto-derived from file path")
    print("=" * 70)


if __name__ == "__main__":
    main()
