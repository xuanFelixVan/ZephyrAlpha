# [BLUEPRINT] MOD-INF-005 | scripts/ops/normalize_headers.py | §
import os
import re
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

FIELD_ORDER = {name: i for i, name in enumerate(FIELD_NAMES)}
COMMENT_FIELD_RE = re.compile(r"^#\s*\[(\w[\w-]*)\]\s*(.*)")

stability_fixed = 0
headers_normalized = 0
files_fixed = 0


def process_file(filepath: Path):
    global files_fixed

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    lines = content.split("\n")

    header_fields = []
    header_end = 0
    in_header = True

    for i, line in enumerate(lines[:50]):
        m = COMMENT_FIELD_RE.match(line.rstrip())
        if m and m.group(1) in FIELD_NAMES:
            header_fields.append((m.group(1), m.group(2).strip()))
            header_end = i
        elif in_header and line.strip() == "":
            continue
        elif in_header:
            in_header = False

    if not header_fields:
        return

    changed = False

    seen = {}
    for fname, fval in header_fields:
        if fname in seen:
            changed = True
            break
        seen[fname] = fval

    if len(header_fields) != len(FIELD_NAMES):
        changed = True

    normalized_lines = []
    for fname in FIELD_NAMES:
        if fname in seen:
            val = seen[fname]
            if val:
                normalized_lines.append(f"# [{fname}] {val}")
            else:
                normalized_lines.append(f"# [{fname}]")

    code_start = header_end + 1
    while code_start < len(lines) and lines[code_start].strip() == "":
        code_start += 1

    code_lines = lines[code_start:]

    new_content_parts = []
    for i, nl in enumerate(normalized_lines):
        new_content_parts.append(nl)
        if i < len(normalized_lines) - 1:
            new_content_parts.append("")

    if code_lines:
        new_content_parts.append("")
        new_content_parts.extend(code_lines)

    result = "\n".join(new_content_parts)
    if result != original:
        changed = True

    if not changed:
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
    print("HEADER NORMALIZATION REPORT")
    print("=" * 70)
    print(f"Files fixed:           {files_fixed}")
    print("=" * 70)


if __name__ == "__main__":
    main()
