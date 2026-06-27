# [BLUEPRINT] MOD-INF-005 | scripts/ops/recover_git_headers.py | §
# [MODULE] scripts.ops.recover_git_headers
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
# [TTL] task_bound
import os
import re
import subprocess
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

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

DEFAULT_VALUES = {
    "STABILITY": "evolving",
    "SAFETY": "L",
    "AI_AUTONOMY": "ai_modifiable",
    "INVARIANTS": "none",
    "MODIFY-GUARD": "none",
}


def is_default_value(field_name, value):
    if field_name in DEFAULT_VALUES and value == DEFAULT_VALUES[field_name]:
        return True
    if field_name in ("CONSUMERS", "ERROR_CONTRACT", "TESTS") and not value:
        return True
    if field_name == "BLUEPRINT" and value.startswith("unknown"):
        return True
    return False


def extract_git_fields(filepath: Path):
    rel = str(filepath.relative_to(REPO_ROOT))
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        if result.returncode != 0:
            return {}
    except (subprocess.TimeoutExpired, Exception):
        return {}

    lines = result.stdout.split("\n")
    fields = {}

    for line in lines[:30]:
        m = COMMENT_FIELD_RE.match(line.rstrip())
        if m and m.group(1) in FIELD_NAMES:
            fields[m.group(1)] = m.group(2).strip()

    for line in lines[:30]:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote_char = stripped[:3]
            after = stripped[3:]
            if after.endswith(quote_char) and len(after) > 3:
                after = after[:-3]
            m = DOCSTRING_FIELD_RE.match(after.strip())
            if m and m.group(1) in FIELD_NAMES and m.group(1) not in fields:
                fields[m.group(1)] = m.group(2).strip()
            break

    return fields


values_restored = 0
files_fixed = 0


def process_file(filepath: Path):
    global files_fixed

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    current_fields = {}
    for i, line in enumerate(lines[:30]):
        m = COMMENT_FIELD_RE.match(line.rstrip())
        if m and m.group(1) in FIELD_NAMES:
            if m.group(1) not in current_fields:
                current_fields[m.group(1)] = (i, m.group(2).strip())

    git_fields = extract_git_fields(filepath)
    if not git_fields:
        return

    changed = False
    for field_name, (line_idx, curr_val) in current_fields.items():
        if field_name in git_fields:
            git_val = git_fields[field_name]
            if is_default_value(field_name, curr_val) and not is_default_value(field_name, git_val) and git_val:
                lines[line_idx] = f"# [{field_name}] {git_val}"
                global values_restored
                values_restored += 1
                changed = True

    if not changed:
        return

    result = "\n".join(lines)
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
    print("GIT RECOVERY REPORT")
    print("=" * 70)
    print(f"Files fixed:       {files_fixed}")
    print(f"Values restored:   {values_restored}")
    print("=" * 70)


if __name__ == "__main__":
    main()
