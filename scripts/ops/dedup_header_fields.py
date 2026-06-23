# [BLUEPRINT] MOD-INF-005 | scripts/ops/dedup_header_fields.py | §
# [MODULE] scripts.ops.dedup_header_fields
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
import os
import re
import sys
from pathlib import Path

SRC_ROOT = Path(r"d:\ZephyrAlpha\src\zephyr")

FIELD_NAMES = [
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

COMMENT_FIELD_RE = re.compile(r"^#\s*\[(\w[\w-]*)\]\s*(.*)")

DEFAULT_VALUES = {
    "STABILITY": "evolving",
    "SAFETY": "L",
    "AI_AUTONOMY": "ai_modifiable",
    "INVARIANTS": "none",
    "MODIFY-GUARD": "none",
}

dups_removed = 0
values_restored = 0
files_fixed = 0


def is_default_value(field_name, value):
    if field_name in DEFAULT_VALUES and value == DEFAULT_VALUES[field_name]:
        return True
    if field_name in ("CONSUMERS", "ERROR_CONTRACT", "TESTS") and not value:
        return True
    if field_name == "BLUEPRINT" and value.startswith("unknown"):
        return True
    return False


def process_file(filepath: Path):
    global files_fixed

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    lines = content.split("\n")

    field_occurrences = {}
    for i, line in enumerate(lines):
        m = COMMENT_FIELD_RE.match(line.rstrip())
        if m and m.group(1) in FIELD_NAMES:
            field_name = m.group(1)
            value = m.group(2).strip()
            if field_name not in field_occurrences:
                field_occurrences[field_name] = []
            field_occurrences[field_name].append((i, value))

    has_duplicates = any(len(v) > 1 for v in field_occurrences.values())
    if not has_duplicates:
        return

    lines_to_remove = set()
    for field_name, occurrences in field_occurrences.items():
        if len(occurrences) <= 1:
            continue

        best_idx = None
        best_value = None
        for idx, value in occurrences:
            if best_idx is None:
                best_idx = idx
                best_value = value
            else:
                curr_is_default = is_default_value(field_name, value)
                best_is_default = is_default_value(field_name, best_value)

                if best_is_default and not curr_is_default:
                    lines_to_remove.add(best_idx)
                    best_idx = idx
                    best_value = value
                    global values_restored
                    values_restored += 1
                elif (not best_is_default and curr_is_default) or (not best_is_default and not curr_is_default):
                    lines_to_remove.add(idx)
                else:
                    lines_to_remove.add(idx)

    if not lines_to_remove:
        return

    global dups_removed
    dups_removed += len(lines_to_remove)

    new_lines = [l for i, l in enumerate(lines) if i not in lines_to_remove]

    result = "\n".join(new_lines)
    if result == original:
        return

    tmp_path = str(filepath) + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(result)
        os.replace(tmp_path, str(filepath))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        print(f"  ERROR: Permission denied writing {filepath}", file=sys.stderr)
        return

    files_fixed += 1
    print(f"  FIXED: {filepath.relative_to(SRC_ROOT)} — removed {len(lines_to_remove)} duplicate field(s)")


def main():
    py_files = sorted(SRC_ROOT.rglob("*.py"))

    for fp in py_files:
        if fp.name == "__init__.py":
            continue
        process_file(fp)

    print("\n" + "=" * 70)
    print("DEDUP PASS REPORT")
    print("=" * 70)
    print(f"Files fixed:           {files_fixed}")
    print(f"Duplicate lines removed: {dups_removed}")
    print(f"Values restored:       {values_restored}")
    print("=" * 70)


if __name__ == "__main__":
    main()
