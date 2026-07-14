# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_n15_blueprint_path.py | §
# [MODULE] scripts.governance.d7_code.fix_n15_blueprint_path
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062104
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只修正 BLUEPRINT 头部路径，不修改文件其他内容
# [MODIFY-GUARD] SPECIAL_CASES 映射变更需 Owner 批准
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=部分失败
# [TESTS] 无
# [TTL] task_bound
"""N-15 BLUEPRINT 头部路径不存在批量修复脚本。

修复内容:
  1. kebab-case 目录名 → snake_case（57 种路径，2888 个违规）
  2. 4 种特殊路径映射（10 个违规）

用法: python scripts/governance/d7_code/fix_n15_blueprint_path.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: N-15 BLUEPRINT 头部路径不存在批量修复脚本。
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
# 特殊路径映射: (old_path, new_path, reason)
# 这些路径无法通过简单的 kebab→snake 转换修复
# ---------------------------------------------------------------------------
SPECIAL_CASES: list[tuple[str, str, str]] = [
    # 1. 缺少 docs/ 前缀 + kebab→snake
    (
        "03_modules/_domain-governance/blueprint.md",
        "docs/03_modules/_domain_governance/blueprint.md",
        "补全 docs/ 前缀 + kebab→snake",
    ),
    # 2. 蓝图文件从未创建，指向最接近的现有文档
    (
        "docs/02_enterprise_architecture/domain-model-migration-plan.md",
        "docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md",
        "原蓝图未创建，指向 phase D 施工计划",
    ),
    # 3. governance 蓝图路径错误，指向 governance_core_blueprint
    (
        "docs/03_modules/_cross_layer/governance/blueprint.md",
        "docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md",
        "governance 蓝图实际位于 shared_core/governance_core_blueprint.md",
    ),
    # 4. 模块路径错误（data → governance）
    (
        "src/zephyr/data/depgraph_reader.py",
        "src/zephyr/governance/depgraph_reader.py",
        "depgraph_reader.py 实际位于 governance/ 而非 data/",
    ),
]

# BLUEPRINT 头部正则: # [BLUEPRINT] MODULE_ID | path | §section
_BLUEPRINT_HEADER_RE = re.compile(
    r"^(\s*#?\s*\[BLUEPRINT\]\s+\S+\s*\|\s*)(\S+)(\s*\|.*)$",
    re.MULTILINE,
)

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

# 跳过的文件扩展名
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
    return False


def kebab_to_snake_path(rel_path: str) -> str:
    """将路径中的目录名从 kebab-case 转为 snake_case。

    保留文件名不变（如 blueprint.md, governance_core_blueprint.md）。
    """
    parts = rel_path.split("/")
    converted_parts = []
    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            # 目录: kebab→snake
            converted_parts.append(part.replace("-", "_"))
        else:
            # 文件名: 保持不变
            converted_parts.append(part)
    return "/".join(converted_parts)


def find_correct_path(old_path: str) -> tuple[str, str] | None:
    """为不存在的路径找到正确的替代路径。

    返回 (new_path, reason) 或 None（无法修复）。
    """
    # 1. 检查特殊映射
    for old, new, reason in SPECIAL_CASES:
        if old_path == old:
            if (REPO_ROOT / new).exists():
                return (new, reason)
            else:
                print(f"  WARNING: 特殊映射目标也不存在: {new}")
                return None

    # 2. 尝试 kebab→snake 转换
    converted = kebab_to_snake_path(old_path)
    if converted != old_path and (REPO_ROOT / converted).exists():
        return (converted, "kebab→snake 转换")

    return None


def fix_file(file_path: Path) -> int:
    """修复单个文件中的 BLUEPRINT 头部路径，返回修复数量。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0

    original = content
    fix_count = 0

    def replace_path(match: re.Match) -> str:
        nonlocal fix_count
        prefix = match.group(1)
        old_path = match.group(2)
        suffix = match.group(3)

        # 如果路径已存在，不修改
        if (REPO_ROOT / old_path).exists():
            return match.group(0)

        # 查找正确路径
        result = find_correct_path(old_path)
        if result is None:
            return match.group(0)

        new_path, reason = result
        fix_count += 1
        rel_file = file_path.relative_to(REPO_ROOT)
        print(f"  FIXED {rel_file}")
        print(f"    {old_path}")
        print(f"    -> {new_path}  [{reason}]")
        return f"{prefix}{new_path}{suffix}"

    content = _BLUEPRINT_HEADER_RE.sub(replace_path, content)

    if content != original:
        try:
            file_path.write_text(content, encoding="utf-8")
            return fix_count
        except Exception as e:
            print(f"  ERROR 写入失败 {file_path}: {e}")
            return 0
    return 0


def main() -> int:
    print("=" * 70)
    print("N-15 BLUEPRINT 头部路径不存在批量修复")
    print("=" * 70)

    # Step 1: 扫描所有 .py 文件并修复
    print("\n[Step 1] 扫描并修复 .py 文件...")
    total_fixed = 0
    files_fixed = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        # 原地修改 dirs 以跳过特定目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = Path(root) / fname
            if should_skip(fpath):
                continue
            count = fix_file(fpath)
            if count > 0:
                files_fixed += 1
                total_fixed += count

    print(f"\n修复完成: {files_fixed} 个文件, {total_fixed} 处路径修正")

    # Step 2: 验证剩余违规
    print("\n[Step 2] 验证剩余 N-15 违规...")
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

    remaining = [l for l in result.stdout.splitlines() if "N-15" in l]
    print(f"剩余 N-15 违规: {len(remaining)}")

    if remaining:
        print("\n前 20 条剩余违规:")
        for line in remaining[:20]:
            print(f"  {line}")

    print("\n" + "=" * 70)
    print(f"修复总结: {files_fixed} 个文件, {total_fixed} 处路径修正")
    print(f"剩余 N-15 违规: {len(remaining)}")
    print("=" * 70)
    return 0 if len(remaining) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
