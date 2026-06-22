# [BLUEPRINT] MOD-INF-005 | scripts/ops/cleanup_duplicate_headers.py | §
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
DOCSTRING_FIELD_RE = re.compile(r"^\[(\w[\w-]*)\]\s*(.*)")

dup_fields_removed = 0
empty_docstrings_removed = 0
blueprints_updated = 0
files_fixed = 0


def process_file(filepath: Path):
    global files_fixed

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    lines = content.split("\n")

    seen_fields = {}
    lines_to_remove = set()

    for i, line in enumerate(lines[:30]):
        m = COMMENT_FIELD_RE.match(line.rstrip())
        if m:
            field_name = m.group(1)
            if field_name in FIELD_NAMES:
                if field_name in seen_fields:
                    prev_idx, prev_val = seen_fields[field_name]
                    curr_val = m.group(2).strip()
                    if curr_val and not prev_val:
                        lines_to_remove.add(prev_idx)
                        seen_fields[field_name] = (i, curr_val)
                    elif (prev_val and not curr_val) or (prev_val and curr_val):
                        lines_to_remove.add(i)
                    else:
                        lines_to_remove.add(i)
                else:
                    seen_fields[field_name] = (i, m.group(2).strip())

    if lines_to_remove:
        global dup_fields_removed
        dup_fields_removed += len(lines_to_remove)
        lines = [l for i, l in enumerate(lines) if i not in lines_to_remove]

    docstring_start = -1
    for i, line in enumerate(lines[:30]):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_start = i
            break

    if docstring_start >= 0:
        quote_char = lines[docstring_start].strip()[:3]
        docstring_end = -1
        for i in range(docstring_start + 1, len(lines)):
            if quote_char in lines[i]:
                docstring_end = i
                break

        if docstring_end >= 0:
            docstring_content = lines[docstring_start : docstring_end + 1]

            has_only_fields_or_empty = True
            non_field_content = []
            for dl in docstring_content:
                stripped = dl.strip()
                if stripped == quote_char:
                    continue
                m = DOCSTRING_FIELD_RE.match(stripped)
                if m and m.group(1) in FIELD_NAMES:
                    continue
                if stripped == "":
                    continue
                has_only_fields_or_empty = False
                non_field_content.append(dl)

            if has_only_fields_or_empty:
                docstring_fields_in_ds = {}
                for dl in docstring_content:
                    stripped = dl.strip()
                    m = DOCSTRING_FIELD_RE.match(stripped)
                    if m and m.group(1) in FIELD_NAMES:
                        docstring_fields_in_ds[m.group(1)] = m.group(2).strip()

                for field_name, value in docstring_fields_in_ds.items():
                    if field_name in seen_fields:
                        prev_idx, prev_val = seen_fields[field_name]
                        if (not prev_val or prev_val.startswith("unknown")) and value:
                            for i, line in enumerate(lines):
                                m2 = COMMENT_FIELD_RE.match(line.rstrip())
                                if m2 and m2.group(1) == field_name:
                                    lines[i] = f"# [{field_name}] {value}"
                                    if field_name == "BLUEPRINT":
                                        global blueprints_updated
                                        blueprints_updated += 1
                                    break

                before = lines[:docstring_start]
                after = lines[docstring_end + 1 :]
                while before and before[-1].strip() == "":
                    before.pop()
                while after and after[0].strip() == "":
                    after.pop(0)
                lines = before + [""] + after
                empty_docstrings_removed += 1

    result = "\n".join(lines)
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
    print(f"  FIXED: {filepath.relative_to(SRC_ROOT)}")


def main():
    py_files = sorted(SRC_ROOT.rglob("*.py"))

    for fp in py_files:
        if fp.name == "__init__.py":
            continue
        process_file(fp)

    print("\n" + "=" * 70)
    print("CLEANUP PASS REPORT")
    print("=" * 70)
    print(f"Files fixed:                  {files_fixed}")
    print(f"Duplicate field lines removed: {dup_fields_removed}")
    print(f"Empty docstrings removed:      {empty_docstrings_removed}")
    print(f"BLUEPRINT values updated:      {blueprints_updated}")
    print("=" * 70)


if __name__ == "__main__":
    main()
