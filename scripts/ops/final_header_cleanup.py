# [BLUEPRINT] MOD-INF-005 | scripts/ops/final_header_cleanup.py | §
# [MODULE] scripts.ops.final_header_cleanup
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
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

FIELD_NAMES = set(
    [
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
)

COMMENT_FIELD_RE = re.compile(r"^#\s*\[(\w[\w-]*)\]\s*(.*)")
DOCSTRING_FIELD_RE = re.compile(r"^\[(\w[\w-]*)\]\s*(.*)")
INLINE_DS_FIELD_RE = re.compile(r'^"""?\s*(\[(\w[\w-]*)\]\s*(.*))')

blueprints_fixed = 0
docstrings_cleaned = 0
files_fixed = 0


def process_file(filepath: Path):
    global files_fixed, blueprints_fixed, docstrings_cleaned

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    lines = content.split("\n")
    changed = False

    docstring_start = -1
    for i, line in enumerate(lines[:30]):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_start = i
            break

    if docstring_start < 0:
        return

    quote_char = lines[docstring_start].strip()[:3]
    docstring_end = -1
    for i in range(docstring_start + 1, len(lines)):
        if quote_char in lines[i]:
            docstring_end = i
            break

    if docstring_end < 0:
        return

    ds_content = lines[docstring_start : docstring_end + 1]
    ds_fields = {}

    for dl in ds_content:
        stripped = dl.strip()
        if stripped.startswith(quote_char):
            after_quote = stripped[len(quote_char) :]
            if after_quote.endswith(quote_char) and len(after_quote) > len(quote_char):
                after_quote = after_quote[: -len(quote_char)]
            m = DOCSTRING_FIELD_RE.match(after_quote.strip())
            if m and m.group(1) in FIELD_NAMES:
                ds_fields[m.group(1)] = m.group(2).strip()
                continue
        m = DOCSTRING_FIELD_RE.match(stripped)
        if m and m.group(1) in FIELD_NAMES:
            ds_fields[m.group(1)] = m.group(2).strip()

    if not ds_fields:
        return

    for field_name, value in ds_fields.items():
        for i, line in enumerate(lines[:30]):
            m = COMMENT_FIELD_RE.match(line.rstrip())
            if m and m.group(1) == field_name:
                curr_val = m.group(2).strip()
                if field_name == "BLUEPRINT" and (curr_val.startswith("unknown") or not curr_val) and value:
                    lines[i] = f"# [BLUEPRINT] {value}"
                    global blueprints_fixed
                    blueprints_fixed += 1
                    changed = True
                break

    non_field_lines = []
    for dl in ds_content:
        stripped = dl.strip()
        if stripped == quote_char:
            continue
        after_quote = stripped
        if after_quote.startswith(quote_char):
            after_quote = after_quote[len(quote_char) :]
        if after_quote.endswith(quote_char):
            after_quote = after_quote[: -len(quote_char)]
        after_quote = after_quote.strip()
        m = DOCSTRING_FIELD_RE.match(after_quote)
        if m and m.group(1) in FIELD_NAMES:
            continue
        if after_quote == "":
            continue
        non_field_lines.append(dl)

    if not non_field_lines:
        before = lines[:docstring_start]
        after = lines[docstring_end + 1 :]
        while before and before[-1].strip() == "":
            before.pop()
        while after and after[0].strip() == "":
            after.pop(0)
        lines = before + [""] + after
        docstrings_cleaned += 1
        changed = True

    if not changed:
        return

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
    print("FINAL CLEANUP REPORT")
    print("=" * 70)
    print(f"Files fixed:                   {files_fixed}")
    print(f"BLUEPRINT values corrected:    {blueprints_fixed}")
    print(f"Empty docstrings removed:      {docstrings_cleaned}")
    print("=" * 70)


if __name__ == "__main__":
    main()
