# [BLUEPRINT] MOD-INF-005 | scripts/ops/migrate_docstring_headers.py | §
import os
import re
import sys
from pathlib import Path

SRC_ROOT = Path(r"d:\ZephyrAlpha\src\zephyr")

FIELD_NAMES = [
    "BLUEPRINT", "MODULE", "INVARIANTS", "MODIFY-GUARD",
    "CONSUMERS", "STABILITY", "SAFETY", "AI_AUTONOMY",
    "ERROR_CONTRACT", "TESTS",
]

FIELD_RE = re.compile(r"^\[(\w[\w-]*)\]\s*(.*)")

files_fixed = 0
files_scanned = 0
fields_migrated = 0
docstrings_cleaned = 0


def find_docstring_end(lines, start_idx):
    closing = '"""'
    for i in range(start_idx + 1, len(lines)):
        if closing in lines[i]:
            return i
    return -1


def process_file(filepath: Path):
    global files_scanned, files_fixed, fields_migrated, docstrings_cleaned
    files_scanned += 1

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    docstring_start = -1
    for i, line in enumerate(lines[:30]):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_start = i
            break

    if docstring_start == -1:
        return

    quote_char = lines[docstring_start].strip()[:3]
    docstring_end = find_docstring_end(lines, docstring_start)
    if docstring_end == -1:
        return

    docstring_lines = lines[docstring_start:docstring_end + 1]

    has_field_in_docstring = False
    docstring_fields = {}
    for dl in docstring_lines:
        m = FIELD_RE.match(dl.strip())
        if m and m.group(1) in FIELD_NAMES:
            has_field_in_docstring = True
            docstring_fields[m.group(1)] = m.group(2).strip()

    if not has_field_in_docstring:
        return

    comment_header_end = docstring_start
    for i in range(docstring_start - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith("# ["):
            comment_header_end = i
            break
        elif stripped == "":
            continue
        else:
            comment_header_end = i + 1
            break

    comment_fields = {}
    for i in range(comment_header_end):
        stripped = lines[i].strip()
        if stripped.startswith("# ["):
            m = re.match(r"^#\s*\[(\w[\w-]*)\]\s*(.*)", stripped)
            if m:
                comment_fields[m.group(1)] = (i, m.group(2).strip())

    new_lines = list(lines)

    for field_name, value in docstring_fields.items():
        if field_name in comment_fields:
            line_idx, old_value = comment_fields[field_name]
            if old_value != value and value:
                new_lines[line_idx] = f"# [{field_name}] {value}"
                fields_migrated += 1
        elif value:
            insert_idx = comment_header_end
            for i in range(comment_header_end - 1, -1, -1):
                if new_lines[i].strip().startswith("# ["):
                    insert_idx = i + 1
                    break
            new_lines.insert(insert_idx, f"# [{field_name}] {value}")
            comment_header_end += 1
            docstring_start += 1
            docstring_end += 1
            fields_migrated += 1

    remaining_docstring = []
    for dl in new_lines[docstring_start:docstring_end + 1]:
        stripped = dl.strip()
        m = FIELD_RE.match(stripped)
        if m and m.group(1) in FIELD_NAMES:
            continue
        remaining_docstring.append(dl)

    non_empty_remaining = [
        l for l in remaining_docstring
        if l.strip() and l.strip() != quote_char and not (l.strip().startswith(quote_char) and l.strip() == quote_char)
    ]

    if not non_empty_remaining:
        before = new_lines[:docstring_start]
        after = new_lines[docstring_end + 1:]
        while before and before[-1].strip() == "":
            before.pop()
        while after and after[0].strip() == "":
            after.pop(0)
        new_lines = before + [""] + after
        docstrings_cleaned += 1
    else:
        cleaned = []
        for dl in remaining_docstring:
            stripped = dl.strip()
            if stripped == "" and cleaned and cleaned[-1].strip() == "":
                continue
            cleaned.append(dl)
        new_lines[docstring_start:docstring_end + 1] = cleaned
        docstrings_cleaned += 1

    result = "\n".join(new_lines)
    if result == content:
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
    print(f"  FIXED: {filepath.relative_to(SRC_ROOT)} — migrated {len(docstring_fields)} fields from docstring")


def main():
    py_files = sorted(SRC_ROOT.rglob("*.py"))

    for fp in py_files:
        if fp.name == "__init__.py":
            continue
        process_file(fp)

    print("\n" + "=" * 70)
    print("DOCSTRING HEADER MIGRATION REPORT")
    print("=" * 70)
    print(f"Files scanned:         {files_scanned}")
    print(f"Files fixed:           {files_fixed}")
    print(f"Fields migrated:       {fields_migrated}")
    print(f"Docstrings cleaned:    {docstrings_cleaned}")
    print("=" * 70)


if __name__ == "__main__":
    main()
