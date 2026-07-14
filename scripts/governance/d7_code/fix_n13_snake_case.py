# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_n13_snake_case.py | §
# [MODULE] scripts.governance.d7_code.fix_n13_snake_case
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062108
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只重命名N-13违规文件，不修改文件内容
# [MODIFY-GUARD] RENAMES/DELETIONS列表变更需Owner批准
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=部分失败
# [TESTS] 无
# [TTL] task_bound
"""N-13 YAML/JSON/MD 文件名 snake_case 批量修复脚本。

修复内容:
  1. 重命名 4 个 index.md → index.md
  2. 重命名 5 个中文文件名 → 英文 snake_case
  3. 删除 1 个遗留存根 blueprint_registry.yaml（真源为 blueprint_registry.yaml）
  4. 重命名 2 个 kebab-case 文件 → snake_case
  5. 更新所有引用

用法: python scripts/governance/d7_code/fix_n13_snake_case.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: N-13 YAML/JSON/MD 文件名 snake_case 批量修复脚本。
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import re
import sys
from pathlib import Path

# REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 一次性 bootstrap sys.path（此 N 值对本文件固定且仅用一次），随后从 _shared.constants 获取 REPO_ROOT。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT

# ---------------------------------------------------------------------------
# 重命名映射: (old_relative_path, new_relative_path)
# ---------------------------------------------------------------------------
RENAMES: list[tuple[str, str]] = [
    # index.md → index.md (4 files)
    ("docs/index.md", "docs/index.md"),
    ("docs/08_knowledge/index.md", "docs/08_knowledge/index.md"),
    ("docs/_working/audit/index.md", "docs/_working/audit/index.md"),
    ("docs/_working/audit/state/index.md", "docs/_working/audit/state/index.md"),
    # Chinese filenames → English snake_case (4 files, ai_team_mode_full_config.md 已删除)
    (
        "docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md",
        "docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md",
    ),
    (
        "docs/02_enterprise_architecture/sample/00_overview_entry_sample.md",
        "docs/02_enterprise_architecture/sample/00_overview_entry_sample.md",
    ),
    (
        "docs/02_enterprise_architecture/sample/04_architecture_principles_decisions_sample.md",
        "docs/02_enterprise_architecture/sample/04_architecture_principles_decisions_sample.md",
    ),
    (
        "docs/02_enterprise_architecture/sample/05_manual_architecture_views_sample.md",
        "docs/02_enterprise_architecture/sample/05_manual_architecture_views_sample.md",
    ),
    # kebab-case → snake_case (1 file, schedule_state.json 已删除)
    (
        "src/zephyr/infrastructure/auto_fix_engine/auto_fix_config.yaml",
        "src/zephyr/infrastructure/auto_fix_engine/auto_fix_config.yaml",
    ),
]

# ---------------------------------------------------------------------------
# 删除映射: (stub_path, real_source_path)
# 存根文件内容为空或占位，真源已存在于下划线版本
# ---------------------------------------------------------------------------
DELETIONS: list[tuple[str, str]] = [
    (
        "docs/03_modules/blueprint_registry.yaml",
        "docs/03_modules/blueprint_registry.yaml",
    ),
]

# ---------------------------------------------------------------------------
# 引用替换规则: (old_pattern, new_pattern, description)
# 用于在文件内容中搜索和替换引用
# ---------------------------------------------------------------------------
REPLACEMENTS: list[tuple[str, str, str]] = [
    # index.md → index.md (全局替换，所有index.md都应改为index.md)
    ("index.md", "index.md", "index.md → index.md"),
    # Chinese filenames → English (ai_team_mode_full_config.md 已删除)
    ("dependency_path_panorama.md", "dependency_path_panorama.md", "中文→英文"),
    ("00_overview_entry_sample.md", "00_overview_entry_sample.md", "中文→英文"),
    ("04_architecture_principles_decisions_sample.md", "04_architecture_principles_decisions_sample.md", "中文→英文"),
    ("05_manual_architecture_views_sample.md", "05_manual_architecture_views_sample.md", "中文→英文"),
    # kebab-case → snake_case (schedule_state.json 已删除)
    ("blueprint_registry.yaml", "blueprint_registry.yaml", "kebab→snake"),
    ("auto_fix_config.yaml", "auto_fix_config.yaml", "kebab→snake"),
]

# 跳过的目录
SKIP_DIRS: set[str] = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".aidrafts",
    ".ailocks",
    "data/backups",
    "data/scans",
    "data/classified",
    "data/security_baselines",
}

# 跳过的文件扩展名（二进制文件）
SKIP_EXTENSIONS: set[str] = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".egg-info",
    ".egg",
    ".whl",
    ".safetensors",
    ".pt",
    ".pth",
    ".model",
    ".onnx",
}


def should_skip(path: Path) -> bool:
    """检查路径是否应跳过。"""
    parts = path.parts
    for skip_dir in SKIP_DIRS:
        if skip_dir in parts:
            return True
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    # 跳过大于 10MB 的文件
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            return True
    except OSError:
        return True
    return False


def update_references_in_file(file_path: Path) -> int:
    """更新单个文件中的引用，返回替换次数。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    original = content
    total_replacements = 0

    for old_str, new_str, _desc in REPLACEMENTS:
        count = content.count(old_str)
        if count > 0:
            content = content.replace(old_str, new_str)
            total_replacements += count

    if content != original:
        try:
            file_path.write_text(content, encoding="utf-8")
            return total_replacements
        except Exception as e:
            print(f"  ERROR 写入失败 {file_path}: {e}")
            return 0
    return 0


def rename_file(old_rel: str, new_rel: str) -> bool:
    """重命名文件。"""
    old_path = REPO_ROOT / old_rel
    new_path = REPO_ROOT / new_rel

    if not old_path.exists():
        print(f"  SKIP 源文件不存在: {old_rel}")
        return False

    if new_path.exists():
        print(f"  SKIP 目标已存在: {new_rel}")
        return False

    # 确保目标目录存在
    new_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        os.replace(str(old_path), str(new_path))
        print(f"  RENAMED {old_rel} → {new_rel}")
        return True
    except OSError as e:
        print(f"  ERROR 重命名失败 {old_rel}: {e}")
        return False


def delete_stub(stub_rel: str, real_rel: str) -> bool:
    """删除存根文件（真源已存在于下划线版本）。"""
    stub_path = REPO_ROOT / stub_rel
    real_path = REPO_ROOT / real_rel

    if not stub_path.exists():
        print(f"  SKIP 存根不存在: {stub_rel}")
        return False

    if not real_path.exists():
        print(f"  ERROR 真源不存在，拒绝删除存根: {real_rel}")
        return False

    try:
        stub_path.unlink()
        print(f"  DELETED {stub_rel} (真源: {real_rel})")
        return True
    except OSError as e:
        print(f"  ERROR 删除失败 {stub_rel}: {e}")
        return False


def main() -> int:
    print("=" * 70)
    print("N-13 YAML/JSON/MD 文件名 snake_case 批量修复")
    print("=" * 70)

    # Step 1: 更新所有引用
    print("\n[Step 1] 更新文件内容中的引用...")
    files_updated = 0
    total_replacements = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        # 原地修改 dirs 以跳过特定目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            if should_skip(fpath):
                continue
            count = update_references_in_file(fpath)
            if count > 0:
                files_updated += 1
                total_replacements += count
                print(f"  UPDATED {fpath.relative_to(REPO_ROOT)} ({count} 处)")

    print(f"\n引用更新完成: {files_updated} 个文件, {total_replacements} 处替换")

    # Step 2: 重命名文件
    print("\n[Step 2] 重命名文件...")
    renamed_count = 0
    for old_rel, new_rel in RENAMES:
        if rename_file(old_rel, new_rel):
            renamed_count += 1
    print(f"重命名完成: {renamed_count}/{len(RENAMES)}")

    # Step 3: 删除存根文件
    print("\n[Step 3] 删除遗留存根文件...")
    deleted_count = 0
    for stub_rel, real_rel in DELETIONS:
        if delete_stub(stub_rel, real_rel):
            deleted_count += 1
    print(f"删除完成: {deleted_count}/{len(DELETIONS)}")

    print("\n" + "=" * 70)
    print(f"修复完成: 重命名 {renamed_count} 个文件, 删除 {deleted_count} 个存根")
    print(f"          更新 {files_updated} 个文件中的 {total_replacements} 处引用")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
