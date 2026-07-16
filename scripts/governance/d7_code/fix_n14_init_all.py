# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_n14_init_all.py | §
# [MODULE] scripts.governance.d7_code.fix_n14_init_all
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062105
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只添加__all__定义，不修改已有内容
# [MODIFY-GUARD] EXEMPT_NAMES列表变更需Owner批准
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=部分失败
# [TESTS] 无
# [TTL] permanent
"""N-14 __init__.py 缺少 __all__ 批量修复脚本。

修复内容:
  1. 扫描所有 __init__.py 文件（排除 tests/, .venv 等）
  2. 检查是否已有 __all__ 定义
  3. 若无，从同目录 .py 文件推导 __all__
  4. 在文件末尾追加 __all__ 定义

用法: python scripts/governance/d7_code/fix_n14_init_all.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: N-14 __init__.py 缺少 __all__ 批量修复脚本。
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

EXEMPT_DIRS: set[str] = {
    "tests",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".git",
    "archive",
    "_reorg_snapshots",
}

EXEMPT_PY_NAMES: set[str] = {
    "__init__.py",
    "__main__.py",
    "setup.py",
    "conftest.py",
}

_ALL_RE = re.compile(r"^__all__\s*[:=]", re.MULTILINE)


def is_exempt(path: Path) -> bool:
    """检查路径是否在豁免目录中。"""
    parts = set(path.parts)
    return bool(parts & EXEMPT_DIRS)


def find_init_files(root: Path) -> list[Path]:
    """查找所有需要修复的 __init__.py 文件。"""
    results: list[Path] = []
    for init_path in root.rglob("__init__.py"):
        if is_exempt(init_path):
            continue
        try:
            content = init_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if not content.strip():
            continue
        if _ALL_RE.search(content):
            continue
        results.append(init_path)
    return results


def derive_all(init_path: Path) -> list[str]:
    """从同目录 .py 文件推导 __all__ 内容。"""
    directory = init_path.parent
    modules: list[str] = []
    for py_file in sorted(directory.iterdir()):
        if not py_file.is_file():
            continue
        name = py_file.name
        if not name.endswith(".py"):
            continue
        if name in EXEMPT_PY_NAMES:
            continue
        if name.startswith("_") and not name.startswith("__"):
            continue
        module_name = name[:-3]
        modules.append(module_name)
    return modules


def add_all_to_file(init_path: Path, all_names: list[str]) -> bool:
    """在 __init__.py 文件末尾追加 __all__ 定义。"""
    try:
        content = init_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [FAIL] 读取失败: {init_path} - {e}")
        return False

    if _ALL_RE.search(content):
        print(f"  [SKIP] 已有 __all__: {init_path}")
        return True

    if all_names:
        names_str = ", ".join(f'"{n}"' for n in all_names)
        all_block = f"\n\n__all__: list[str] = [{names_str}]\n"
    else:
        all_block = "\n\n__all__: list[str] = []\n"

    new_content = content.rstrip() + all_block

    tmp_path = init_path.with_suffix(".py.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, init_path)
    except Exception as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        print(f"  [FAIL] 写入失败: {init_path} - {e}")
        return False

    print(f"  [OK] 添加 __all__ ({len(all_names)} 个模块): {init_path}")
    return True


def verify_fixes() -> int:
    """验证修复结果：N-14 违规数应为 0。"""
    import subprocess

    check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
    result = subprocess.run(
        [sys.executable, str(check_script), "--scan", "--warn-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
    )
    n14_lines = [line for line in result.stdout.splitlines() if "N-14" in line]
    count = len(n14_lines)
    print(f"\nN-14 violations: {count}")
    if count == 0:
        print("[OK] N-14 修复验证通过")
        return 0
    print("[FAIL] N-14 仍有违规:")
    for line in n14_lines[:10]:
        print(f"  {line}")
    return 1


def main() -> int:
    print("=" * 60)
    print("N-14 __init__.py 缺少 __all__ 批量修复脚本")
    print("=" * 60)
    print()

    scan_dirs = [
        REPO_ROOT / "src",
        REPO_ROOT / "docs",
        REPO_ROOT / "scripts",
    ]

    all_init_files: list[Path] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        print(f"扫描: {scan_dir}")
        found = find_init_files(scan_dir)
        print(f"  发现 {len(found)} 个需要修复的 __init__.py")
        all_init_files.extend(found)

    print(f"\n总计: {len(all_init_files)} 个 __init__.py 需要修复")
    print()

    success_count = 0
    fail_count = 0
    for init_path in all_init_files:
        all_names = derive_all(init_path)
        if add_all_to_file(init_path, all_names):
            success_count += 1
        else:
            fail_count += 1

    print()
    print(f"修复完成: 成功 {success_count}, 失败 {fail_count}")
    print()

    if fail_count > 0:
        print("[WARN] 有失败项，请检查上述输出")

    print("验证修复结果...")
    return verify_fixes()


if __name__ == "__main__":
    sys.exit(main())
