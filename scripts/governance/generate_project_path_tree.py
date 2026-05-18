# [BLUEPRINT] MOD-INF-037 | docs/03_modules/l01_infrastructure/registry-governance/blueprint.md | §
# [MODULE] scripts.governance.generate_project_path_tree
# [INVARIANTS] 
# [MODIFY-GUARD] 
# [CONSUMERS] 
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 
# [TESTS] 
"""从磁盘扫描生成 project-path-tree.yaml 物理路径树快照。

对标: Bazel BUILD 文件聚合 + Google Piper 目录视图。
生成物: docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml

用法:
    python scripts/governance/generate_project_path_tree.py            # stdout
    python scripts/governance/generate_project_path_tree.py --write    # 覆写
    python scripts/governance/generate_project_path_tree.py --check    # CI 漂移检测
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "project-path-tree.yaml"
)

SCAN_ROOTS = ["src/zephyr", "scripts", "tests", "config", "docs"]
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    ".audit_cache",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    ".idea",
    ".vs",
    ".eggs",
    "*.egg-info",
}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".so", ".dll", ".exe", ".obj", ".pdb", ".idb"}
MAX_DEPTH = 8

logger = logging.getLogger(__name__)


def _should_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    if name.endswith(".egg-info"):
        return True
    return False


def scan_directory(root: Path, prefix: str = "", depth: int = 0) -> dict:
    if depth > MAX_DEPTH:
        return {"__truncated__": True}

    dirs: dict[str, dict] = {}
    files: list[str] = []

    try:
        entries = sorted(root.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return {"__permission_denied__": True}

    for entry in entries:
        if entry.name.startswith(".") and entry.name not in {".env", ".pre-commit-config.yaml"}:
            continue
        if entry.is_dir():
            if _should_skip_dir(entry.name):
                continue
            subdir = scan_directory(entry, prefix=f"{prefix}/{entry.name}", depth=depth + 1)
            if subdir:
                dirs[entry.name] = subdir
        elif entry.is_file():
            if entry.suffix in SKIP_EXTENSIONS:
                continue
            files.append(entry.name)

    result: dict = {}
    if files:
        result["__files__"] = files
        result["__file_count__"] = len(files)
    if dirs:
        result.update(dirs)
    return result


def count_tree(tree: dict) -> tuple[int, int]:
    file_count = tree.get("__file_count__", 0)
    dir_count = 0
    for key, val in tree.items():
        if key.startswith("__"):
            continue
        if isinstance(val, dict):
            dir_count += 1
            fc, dc = count_tree(val)
            file_count += fc
            dir_count += dc
    return file_count, dir_count


def tree_to_yaml(tree: dict, indent: int = 4) -> str:
    lines: list[str] = []

    file_list = tree.get("__files__")
    if file_list:
        lines.append(" " * indent + "__files__:")
        for f in file_list:
            escaped = f.replace("'", "''")
            lines.append(" " * (indent + 2) + f"- '{escaped}'")

    for key in sorted(tree.keys()):
        if key.startswith("__"):
            continue
        val = tree[key]
        if isinstance(val, dict):
            lines.append(" " * indent + f"{key}/:")
            lines.append(tree_to_yaml(val, indent + 2))

    return "\n".join(lines)


def generate_yaml() -> str:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_files = 0
    total_dirs = 0
    sections: list[str] = []

    for root_name in SCAN_ROOTS:
        root_path = PROJECT_ROOT / root_name
        if not root_path.exists():
            sections.append(f"  {root_name}/:\n    _status: absent")
            continue
        tree = scan_directory(root_path, prefix=root_name)
        fc, dc = count_tree(tree)
        total_files += fc
        total_dirs += dc
        section = f"  {root_name}/:\n{tree_to_yaml(tree, 4)}"
        sections.append(section)

    header = (
        "# ============================================================================\n"
        "# ZephyrAlpha 物理路径树快照 — 自动生成，禁止手写\n"
        "# 生成工具: scripts/governance/generate_project_path_tree.py\n"
        "# 用途: AI 冷启动第一步——'项目现在长什么样'\n"
        "# ============================================================================\n\n"
    )

    meta = (
        f"meta:\n"
        f"  generated_at: '{now}'\n"
        f"  auto_generated_by: 'scripts/governance/generate_project_path_tree.py'\n"
        f"  total_files: {total_files}\n"
        f"  total_directories: {total_dirs}\n"
        f"  scan_roots: {SCAN_ROOTS}\n"
        f"  max_depth: {MAX_DEPTH}\n\n"
    )

    body = "tree:\n" + "\n".join(sections) + "\n"

    return header + meta + body


def cmd_write() -> None:
    content = generate_yaml()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{OUTPUT_FILE}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, OUTPUT_FILE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
    print(f"[OK] Written to {OUTPUT_FILE}")


def cmd_check() -> None:
    if not OUTPUT_FILE.exists():
        print("[FAIL] project-path-tree.yaml does not exist. Run with --write first.")
        sys.exit(1)
    generated = generate_yaml()
    current = OUTPUT_FILE.read_text(encoding="utf-8")
    gen_stripped = re.sub(r"generated_at: '[^']*'", "generated_at: ''", generated)
    cur_stripped = re.sub(r"generated_at: '[^']*'", "generated_at: ''", current)
    if cur_stripped.strip() != gen_stripped.strip():
        print("[FAIL] project-path-tree.yaml is OUT OF SYNC with disk.")
        print("       Run: python scripts/governance/generate_project_path_tree.py --write")
        sys.exit(1)
    else:
        print("[OK] project-path-tree.yaml is in sync with disk.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project-path-tree.yaml")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="Overwrite registry file")
    group.add_argument("--check", action="store_true", help="CI mode: exit 1 if mismatch")
    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.write:
        cmd_write()
    else:
        print(generate_yaml())


if __name__ == "__main__":
    main()
