# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_n12_ke_naming.py | §
# [MODULE] scripts.governance.d7_code.fix_n12_ke_naming
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062103
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只重命名N-12违规文件+更新引用，不修改文件内容
# [MODIFY-GUARD] 无
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=部分失败
# [TESTS] 无
# [TTL] permanent
"""N-12 KE 条目命名格式批量修复脚本。

修复内容:
  1. 将 ke-NNN-kebab-case-title.md 重命名为 ke-NNN-snake_case_title.md
  2. 更新所有文件中对旧文件名的引用

命名规则真源: trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot (snake_case)

用法: python scripts/governance/d7_code/fix_n12_ke_naming.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: N-12 KE 条目命名格式批量修复脚本。
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

# KE 文件名模式: ke-{1-4位数字}-{snake_case_title}.md
KE_VALID_PATTERN = re.compile(r"^ke-\d{1,4}-[a-z][a-z0-9_]+\.md$")
# KE 文件名前缀模式: ke-{数字}-
KE_PREFIX_RE = re.compile(r"^ke-(\d{1,4})-(.+)$", re.IGNORECASE)

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
    ".egg-info",
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
    ".egg",
    ".whl",
    ".safetensors",
    ".pt",
    ".pth",
    ".model",
    ".onnx",
}


def is_ke_violation(filename: str) -> bool:
    """检查文件名是否违反 N-12 规则。"""
    if not filename.lower().startswith("ke-"):
        return False
    if not filename.lower().endswith(".md"):
        return False
    # 如果已经符合 snake_case 模式，不是违规
    if KE_VALID_PATTERN.match(filename.lower()):
        return False
    # 检查是否是 ke-NNN-... 格式
    m = KE_PREFIX_RE.match(filename)
    if not m:
        return False
    return True


def kebab_to_snake_filename(filename: str) -> str:
    """将 ke-NNN-kebab-title.md 转为 ke-NNN-snake_title.md。"""
    m = KE_PREFIX_RE.match(filename)
    if not m:
        return filename
    num = m.group(1)
    rest = m.group(2)
    # 将 title 部分的 - 替换为 _
    snake_rest = rest.replace("-", "_")
    return f"ke-{num}-{snake_rest}"


def find_ke_files(root: Path) -> list[tuple[Path, str, str]]:
    """查找所有违反 N-12 的 KE 文件。

    返回 [(file_path, old_name, new_name), ...]
    """
    violations = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        rel_dir = str(Path(dirpath)).replace("\\", "/").lower()
        if "08_knowledge/" not in rel_dir and "knowledge" not in rel_dir:
            continue

        for fname in files:
            if is_ke_violation(fname):
                new_name = kebab_to_snake_filename(fname)
                if new_name != fname:
                    violations.append((Path(dirpath) / fname, fname, new_name))

    return violations


def update_references_in_file(file_path: Path, rename_map: dict[str, str]) -> int:
    """更新单个文件中的引用，返回替换次数。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    original = content
    total_replacements = 0

    for old_name, new_name in rename_map.items():
        count = content.count(old_name)
        if count > 0:
            content = content.replace(old_name, new_name)
            total_replacements += count

    if content != original:
        try:
            file_path.write_text(content, encoding="utf-8")
            return total_replacements
        except Exception as e:
            print(f"  ERROR 写入失败 {file_path}: {e}")
            return 0
    return 0


def should_skip_file(path: Path) -> bool:
    """检查路径是否应跳过（用于引用更新扫描）。"""
    parts = path.parts
    for skip_dir in SKIP_DIRS:
        if skip_dir in parts:
            return True
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            return True
    except OSError:
        return True
    return False


def main() -> int:
    print("=" * 70)
    print("N-12 KE 条目命名格式批量修复")
    print("=" * 70)

    # Step 1: 查找所有违规文件
    print("\n[Step 1] 查找 N-12 违规文件...")
    violations = find_ke_files(REPO_ROOT)
    print(f"找到 {len(violations)} 个违规文件")

    if not violations:
        print("无需修复")
        return 0

    # 构建重命名映射
    rename_map: dict[str, str] = {}
    rename_pairs: list[tuple[Path, Path]] = []
    for fpath, old_name, new_name in violations:
        new_path = fpath.parent / new_name
        rename_map[old_name] = new_name
        rename_pairs.append((fpath, new_path))

    # 检查冲突（新文件名已存在）
    conflicts = []
    for old_path, new_path in rename_pairs:
        if new_path.exists() and old_path != new_path:
            conflicts.append((old_path, new_path))
    if conflicts:
        print(f"\nWARNING: {len(conflicts)} 个冲突（目标文件已存在）:")
        for old_path, new_path in conflicts[:10]:
            print(f"  {old_path.name} -> {new_path.name} (目标已存在)")
        # 跳过冲突文件
        rename_pairs = [(o, n) for o, n in rename_pairs if not (n.exists() and o != n)]
        print(f"跳过冲突后剩余: {len(rename_pairs)} 个文件")

    # Step 2: 更新所有引用
    print(f"\n[Step 2] 更新文件内容中的引用 ({len(rename_map)} 个文件名)...")
    files_updated = 0
    total_replacements = 0

    for dirpath, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(dirpath) / fname
            if should_skip_file(fpath):
                continue
            count = update_references_in_file(fpath, rename_map)
            if count > 0:
                files_updated += 1
                total_replacements += count

    print(f"引用更新完成: {files_updated} 个文件, {total_replacements} 处替换")

    # Step 3: 重命名文件
    print(f"\n[Step 3] 重命名文件...")
    renamed_count = 0
    for old_path, new_path in rename_pairs:
        try:
            os.replace(str(old_path), str(new_path))
            renamed_count += 1
        except OSError as e:
            print(f"  ERROR 重命名失败 {old_path.name}: {e}")

    print(f"重命名完成: {renamed_count}/{len(rename_pairs)}")

    # Step 4: 验证
    print("\n[Step 4] 验证剩余 N-12 违规...")
    import subprocess

    result = subprocess.run(
        [
            "python",
            "scripts/governance/d3_metadata/check_naming_convention.py",
            "--scan",
            "--warn-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
    )

    remaining = [l for l in result.stdout.splitlines() if "N-12" in l]
    print(f"剩余 N-12 违规: {len(remaining)}")

    if remaining:
        print("\n前 20 条剩余违规:")
        for line in remaining[:20]:
            print(f"  {line}")

    print("\n" + "=" * 70)
    print(f"修复总结: 重命名 {renamed_count} 个文件, 更新 {files_updated} 个文件中的 {total_replacements} 处引用")
    print(f"剩余 N-12 违规: {len(remaining)}")
    print("=" * 70)
    return 0 if len(remaining) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
