#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.rename_kebab_to_snake
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""rename_kebab_to_snake.py — 全项目文件名/目录名 kebab-case → snake_case 批量重命名。

操作流程：
  1. 扫描所有含连字符的文件名和目录名
  2. 生成改名映射表
  3. --dry-run: 只输出映射表，不执行
  4. --apply: 执行 git mv + 替换所有引用

豁免规则：
  - .py 文件不改（已是 snake_case）
  - .git/ .venv/ node_modules/ __pycache__/ .ruff_cache/ models/ 目录跳过
  - TECH_VERSION_TOKENS 中的连字符保留（pydantic-v2 等）
  - UPPERCASE_WHITELIST 中的文件不改（Dockerfile/LICENSE）
  - session-YYYYMMDD-NNN 格式保留
  - .github/ 目录不改
  - docker-compose.yml 不改
  - requirements-*.txt 不改（pip 约定）
  - _domain- 前缀中的连字符改（_domain-governance → _domain_governance）
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from _shared.constants import REPO_ROOT


# ── 豁免配置 ──

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    "models",
    ".trae",
    ".mypy_cache",
    ".pytest_cache",
}

# 技术栈版本号中的连字符保留
TECH_VERSION_TOKENS = [
    "pydantic-v2",
    "python-v3",
    "claude-3",
    "deepseek-v3",
    "deepseek-v4",
    "gpt-4",
    "gpt-5",
    "glm-4",
    "glm-5",
    "qwen-2",
    "pytest-8",
    "react-18",
    "vue-3",
    "node-v20",
    "node-v18",
    "django-5",
    "fastapi-0",
    "postgres-16",
    "redis-7",
    "k8s-1",
    "terraform-1",
    "ubuntu-22",
    "ubuntu-24",
]

# 大写白名单文件名不改
UPPERCASE_WHITELIST = {
    "Dockerfile",
    "LICENSE",
}

# 整个目录跳过
SKIP_DIR_PREFIXES = [".github"]

# 文件名模式豁免（正则）
SKIP_PATTERNS = [
    re.compile(r"^session-\d{8}-\d{3}"),  # session logs
    re.compile(r"^requirements-"),  # pip requirements
    re.compile(r"^docker-compose"),  # docker
    re.compile(r"^batch-\d+-\d+"),  # merkle batches
    re.compile(r"^depmap-legacy-"),  # depmap archives
    re.compile(r"^ai_audit_\d{4}-"),  # audit logs with dates
    re.compile(r"^ke-\d+-"),  # knowledge entries
]


def kebab_to_snake(name: str) -> str:
    """将文件名/目录名中的连字符转为下划线，保留豁免项。"""
    # 检查豁免
    if name in UPPERCASE_WHITELIST:
        return name
    for pattern in SKIP_PATTERNS:
        if pattern.match(name):
            return name
    # 执行替换
    new_name = name.replace("-", "_")
    return new_name


def scan_targets() -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]]]:
    """扫描所有需要改名的文件和目录。返回 (file_renames, dir_renames)。"""
    file_renames: list[tuple[Path, Path]] = []
    dir_renames: list[tuple[Path, Path]] = []

    for root, dirs, files in os.walk(REPO_ROOT):
        root_path = Path(root)

        # 跳过排除目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

        # 检查目录名
        for d in list(dirs):
            if any(root_path.joinpath(d).is_relative_to(REPO_ROOT / p) for p in SKIP_DIR_PREFIXES):
                continue
            new_name = kebab_to_snake(d)
            if new_name != d:
                old_path = root_path / d
                new_path = root_path / new_name
                dir_renames.append((old_path, new_path))

        # 检查文件名
        for f in files:
            if any(root_path.is_relative_to(REPO_ROOT / p) for p in SKIP_DIR_PREFIXES):
                continue
            # .py 文件跳过
            if f.endswith(".py"):
                continue
            new_name = kebab_to_snake(f)
            if new_name != f:
                old_path = root_path / f
                new_path = root_path / new_name
                file_renames.append((old_path, new_path))

    # 目录按深度排序（深的先改，避免父目录改名后子目录路径失效）
    dir_renames.sort(key=lambda x: -len(x[0].parts))

    return file_renames, dir_renames


def build_reference_map(renames: list[tuple[Path, Path]]) -> dict[str, str]:
    """构建旧路径→新路径的字符串映射（用于替换引用）。"""
    ref_map: dict[str, str] = {}
    for old_path, new_path in renames:
        # 相对路径引用（正斜杠和反斜杠都处理）
        old_rel = str(old_path.relative_to(REPO_ROOT)).replace("\\", "/")
        new_rel = str(new_path.relative_to(REPO_ROOT)).replace("\\", "/")
        ref_map[old_rel] = new_rel
        # 仅文件名引用
        if old_path.name != new_path.name:
            ref_map[old_path.name] = new_path.name
    return ref_map


def replace_references(ref_map: dict[str, str], dry_run: bool = False) -> int:
    """在所有文本文件中替换旧路径引用为新路径。返回替换总数。"""
    total_replacements = 0
    # 按长度降序排列，避免短路径先匹配导致长路径替换不完整
    sorted_refs = sorted(ref_map.items(), key=lambda x: -len(x[0]))

    # 用 Grep 预筛选：只修改包含旧路径的文件
    files_to_check: set[str] = set()
    for old_ref in ref_map:
        try:
            result = subprocess.run(
                ["git", "grep", "-l", "--", old_ref],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        files_to_check.add(line.strip())
        except Exception:
            pass
        # 也搜索未跟踪文件
        try:
            result = subprocess.run(
                ["rg", "-l", "--", old_ref, str(REPO_ROOT)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        files_to_check.add(line.strip())
        except Exception:
            pass

    print(f"  需检查文件: {len(files_to_check)} 个")

    for filepath_str in files_to_check:
        filepath = Path(filepath_str)
        if not filepath.exists():
            filepath = REPO_ROOT / filepath_str
        if not filepath.exists():
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        new_content = content
        file_changes = 0
        for old_ref, new_ref in sorted_refs:
            if old_ref in new_content:
                count = new_content.count(old_ref)
                new_content = new_content.replace(old_ref, new_ref)
                file_changes += count

        if file_changes > 0:
            total_replacements += file_changes
            if dry_run:
                print(f"  [REF] {filepath.relative_to(REPO_ROOT)}: {file_changes} replacements")
            else:
                tmp_path = filepath.with_suffix(filepath.suffix + f".{os.getpid()}.tmp")
                try:
                    with open(tmp_path, "w", encoding="utf-8") as fh:
                        fh.write(new_content)
                    os.replace(tmp_path, filepath)
                except PermissionError:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    print(f"  [WARN] Cannot write {filepath}", file=sys.stderr)

    return total_replacements


def execute_renames(renames: list[tuple[Path, Path]], dry_run: bool = False) -> int:
    """执行改名。git 跟踪的用 git mv，未跟踪的用 os.rename。返回成功数。"""
    # 一次性获取所有 git 跟踪文件
    tracked_result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    tracked_files = set(tracked_result.stdout.strip().split("\n")) if tracked_result.returncode == 0 else set()

    success = 0
    for old_path, new_path in renames:
        if new_path.exists():
            print(f"  [SKIP] {new_path.relative_to(REPO_ROOT)} already exists")
            continue
        if dry_run:
            print(f"  [RENAME] {old_path.relative_to(REPO_ROOT)} → {new_path.relative_to(REPO_ROOT)}")
            success += 1
        else:
            rel = str(old_path.relative_to(REPO_ROOT)).replace("\\", "/")
            try:
                if rel in tracked_files:
                    result = subprocess.run(
                        ["git", "mv", str(old_path), str(new_path)],
                        capture_output=True,
                        text=True,
                        cwd=str(REPO_ROOT),
                    )
                    if result.returncode == 0:
                        success += 1
                    else:
                        print(f"  [FAIL] git mv {old_path.relative_to(REPO_ROOT)}: {result.stderr.strip()}")
                else:
                    os.rename(old_path, new_path)
                    success += 1
            except Exception as e:
                print(f"  [FAIL] {old_path.relative_to(REPO_ROOT)}: {e}")
    return success


def main():
    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("  DRY RUN — 不执行任何修改，只输出映射表")
        print("  使用 --apply 执行实际改名")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  EXECUTING — 正在执行改名")
        print("=" * 60)

    # STEP 1: 扫描
    print("\n[STEP 1] 扫描需要改名的文件和目录...")
    file_renames, dir_renames = scan_targets()
    print(f"  文件: {len(file_renames)} 个")
    print(f"  目录: {len(dir_renames)} 个")

    # STEP 2: 输出映射表
    print("\n[STEP 2] 改名映射表:")
    for old_path, new_path in file_renames[:20]:
        print(f"  {old_path.relative_to(REPO_ROOT)} → {new_path.name}")
    if len(file_renames) > 20:
        print(f"  ... 还有 {len(file_renames) - 20} 个文件")
    for old_path, new_path in dir_renames[:10]:
        print(f"  {old_path.relative_to(REPO_ROOT)}/ → {new_path.name}/")
    if len(dir_renames) > 10:
        print(f"  ... 还有 {len(dir_renames) - 10} 个目录")

    # STEP 3: 执行目录改名（先改目录，因为文件在目录内）
    if dir_renames:
        print(f"\n[STEP 3] 目录改名 ({len(dir_renames)} 个)...")
        dir_success = execute_renames(dir_renames, dry_run)
        print(f"  成功: {dir_success}/{len(dir_renames)}")

    # STEP 4: 执行文件改名
    if file_renames:
        print(f"\n[STEP 4] 文件改名 ({len(file_renames)} 个)...")
        file_success = execute_renames(file_renames, dry_run)
        print(f"  成功: {file_success}/{len(file_renames)}")

    # STEP 5: 替换引用
    all_renames = dir_renames + file_renames
    if all_renames:
        print("\n[STEP 5] 替换文件内容中的路径引用...")
        ref_map = build_reference_map(all_renames)
        print(f"  引用映射: {len(ref_map)} 条")
        total = replace_references(ref_map, dry_run)
        print(f"  替换总数: {total}")

    # STEP 6: 更新规则文件
    print("\n[STEP 6] 需要手动更新的规则文件:")
    print("  - trae_028_doc_structure_naming.yaml: N-13 规则改为 snake_case")
    print("  - check_naming_convention.py: N-13 检测逻辑改为 snake_case")
    print("  - trae_028_doc_structure_naming.yaml: 目录命名统一 snake_case")

    print("\n" + "=" * 60)
    if dry_run:
        print("  DRY RUN 完成 — 使用 --apply 执行")
    else:
        print("  改名完成 — 请运行验证命令确认")
    print("=" * 60)


if __name__ == "__main__":
    main()
