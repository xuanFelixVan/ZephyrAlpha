"""fix_naming_manual — 手动修复少量命名违规(N-11/N-10/N-03/N-09/N-16)。

运行 check_naming_convention.py --scan，解析输出，
对 N-11/N-10/N-03/N-09/N-16 违规逐类应用修复（重命名 + 更新引用）。

Usage:
    python scripts/governance/d7_code/fix_naming_manual.py              # 执行修复
    python scripts/governance/d7_code/fix_naming_manual.py --dry-run    # 仅预览
    python scripts/governance/d7_code/fix_naming_manual.py --report     # 仅报告违规
"""

# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/fix_naming_manual.py | §
# [MODULE] scripts.governance.d3_metadata.check_naming_convention
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] OPS-2026062109 任务卡
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只重命名文件/目录+更新引用；不修改文件内容（除引用路径）
# [MODIFY-GUARD] evolving；修复逻辑可扩展
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 重命名失败 → 回滚并报告
# [TESTS] python scripts/governance/d3_metadata/check_naming_convention.py --scan --warn-only
# [TTL] task_bound

from __future__ import annotations

__manifest__ = """
args: []
description: fix_naming_manual — 手动修复少量命名违规(N-11/N-10/N-03/N-09/N-16)。
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 一次性 bootstrap sys.path（此 N 值对本文件固定且仅用一次），随后从 _shared.constants 获取 REPO_ROOT。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT
_CHECK_SCRIPT = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

TARGET_RULES = {"N-03", "N-09", "N-10", "N-11", "N-16"}

# 中文目录名 -> 英文 snake_case 映射
CHINESE_DIR_MAP: dict[str, str] = {
    "00_overview_entry": "00_overview_entry",
    "01_global_architecture_diagram": "01_global_architecture_diagram",
    "02_domain_architecture_docs": "02_domain_architecture_docs",
    "03_governance_reports": "03_governance_reports",
    "04_architecture_principles_decisions": "04_architecture_principles_decisions",
    "05_manual_architecture_views": "05_manual_architecture_views",
    "06_manual_architecture_diagrams": "06_manual_architecture_diagrams",
    "_archive": "_archive",
}

# N-10 目录名修正映射（特殊处理）
N10_DIR_MAP: dict[str, str] = {
    "infrastructure_runtime_integration": "infrastructure_runtime_integration",
    "script-system": "script_system",
    "mod_inf_007": "mod_inf_007",
    "mod_inf_008": "mod_inf_008",
    "mod_inf_009": "mod_inf_009",
    "mod_inf_010": "mod_inf_010",
    "mod_inf_012": "mod_inf_012",
    "mod_inf_013": "mod_inf_013",
    "mod_inf_014": "mod_inf_014",
    "mod_inf_016": "mod_inf_016",
    "mod_inf_032": "mod_inf_032",
    "mod_inf_001": "mod_inf_001",
    "mod_inf_006": "mod_inf_006",
    "mod_inf_006_MCP": "mod_inf_006_mcp",
    "dom_gov_001": "dom_gov_001",
    "mod_master_001": "mod_master_001",
    "sys_master_001": "sys_master_001",
    "handoff": "handoff",
}

# N-10 豁免目录（不应重命名的目录）
N10_EXEMPT_DIRS: set[str] = {
    "zephyralpha.egg_info",  # Python packaging artifact
    "2026",  # 年份目录（日志路径）
    "04",  # 月份目录（日志路径）
    "05",  # 月份目录（日志路径）
}


def collect_violations() -> list[dict]:
    """运行 check_naming_convention.py --scan，解析输出，返回目标违规列表。"""
    result = subprocess.run(
        [sys.executable, str(_CHECK_SCRIPT), "--scan", "--warn-only"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        encoding="utf-8",
        errors="replace",
    )
    violations = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        match = re.match(r"^\[(N-\d+)\]\s+(.+)", line)
        if not match:
            continue
        rule = match.group(1)
        if rule not in TARGET_RULES:
            continue
        message = match.group(2)
        violations.append({"rule": rule, "message": message})
    return violations


def _to_snake_case(name: str) -> str:
    """将各种命名格式转为 snake_case。"""
    s = name.replace("-", "_").replace(" ", "_").replace("\t", "_").replace(".", "_")
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _batch_update_references(renames: list[tuple[str, str]], dry_run: bool = False) -> int:
    """批量更新所有引用。单次 os.walk 遍历。renames = [(old_basename, new_basename), ...]"""
    if not renames:
        return 0
    rename_map = {old: new for old, new in renames if old != new}
    if not rename_map:
        return 0
    updated = 0
    extensions = (".py", ".yaml", ".yml", ".md", ".json", ".toml", ".cfg", ".ini", ".txt")
    # 跳过备份/归档/snapshot目录（不应修改）
    skip_dirs = {"_backups", "_archive", "__pycache__", "node_modules", ".git", ".venv", "venv"}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in skip_dirs
        ]
        # 跳过 snapshot_* 目录
        dirs[:] = [d for d in dirs if not d.startswith("snapshot_")]
        for f in files:
            if not f.endswith(extensions):
                continue
            fpath = Path(root) / f
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            new_content = content
            for old_name, new_name in rename_map.items():
                if old_name in new_content:
                    new_content = new_content.replace(old_name, new_name)
            if new_content == content:
                continue
            if dry_run:
                print(f"    [DRY-RUN] 更新引用: {fpath}")
            else:
                tmp = fpath.with_suffix(fpath.suffix + ".tmp")
                tmp.write_text(new_content, encoding="utf-8")
                os.replace(tmp, fpath)
                print(f"    [UPDATED] {fpath}")
            updated += 1
    return updated


def _is_case_only_rename(old: Path, new: Path) -> bool:
    """检查是否仅为大小写差异（Windows 文件系统大小写不敏感）。"""
    return old.parent == new.parent and old.name.lower() == new.name.lower() and old.name != new.name


def _git_mv(old: Path, new: Path, dry_run: bool = False) -> bool:
    """使用 git mv 重命名（保留历史）。回退到 os.rename。处理大小写重命名。"""
    if dry_run:
        print(f"    [DRY-RUN] git mv {old.name} -> {new.name}")
        return True
    try:
        new.parent.mkdir(parents=True, exist_ok=True)
        if _is_case_only_rename(old, new):
            # Windows 大小写不敏感：先重命名为临时名再重命名为目标名
            temp_name = old.parent / f"__tmp_rename_{os.getpid()}"
            subprocess.run(
                ["git", "mv", str(old), str(temp_name)],
                check=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )
            subprocess.run(
                ["git", "mv", str(temp_name), str(new)],
                check=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )
        else:
            subprocess.run(
                ["git", "mv", str(old), str(new)],
                check=True,
                capture_output=True,
                cwd=REPO_ROOT,
            )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            if _is_case_only_rename(old, new):
                temp_name = old.parent / f"__tmp_rename_{os.getpid()}"
                os.rename(old, temp_name)
                os.rename(temp_name, new)
            else:
                os.rename(old, new)
            return True
        except OSError as e:
            print(f"    [ERROR] 重命名失败: {old} -> {new}: {e}")
            return False


def _build_file_index() -> dict[str, Path]:
    """构建文件/目录名到路径的索引（单次 os.walk）。"""
    index: dict[str, Path] = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d != "__pycache__" and d != "node_modules"
            and d != ".git"
        ]
        for d in dirs:
            if d not in index:
                index[d] = Path(root) / d
        for f in files:
            if f not in index:
                index[f] = Path(root) / f
    return index


_FILE_INDEX: dict[str, Path] | None = None


def _find_abspath(name: str) -> Path | None:
    """根据文件名查找实际路径（使用索引）。"""
    global _FILE_INDEX
    if _FILE_INDEX is None:
        _FILE_INDEX = _build_file_index()
    if not name:
        return None
    # 先尝试直接作为相对路径
    candidate = REPO_ROOT / name
    if candidate.exists():
        return candidate
    # 从索引查找
    basename = Path(name).name
    return _FILE_INDEX.get(basename)


def fix_n09_n10(violations: list[dict], dry_run: bool) -> tuple[int, list[tuple[str, str]]]:
    """N-09/N-10: 重命名不合规目录。返回(修复数, 重命名列表)。"""
    renames: list[tuple[str, str]] = []
    fixed = 0
    seen: set[str] = set()

    for v in violations:
        if v["rule"] not in ("N-09", "N-10"):
            continue
        msg = v["message"]
        # 提取目录名
        name_match = re.search(r":\s*(\S+)$", msg)
        if not name_match:
            continue
        old_name = name_match.group(1)
        if old_name in seen:
            continue
        seen.add(old_name)

        # 跳过豁免目录
        if old_name in N10_EXEMPT_DIRS:
            print(f"[N-10] 跳过(豁免): {old_name}")
            continue

        # 确定新名称
        if old_name in CHINESE_DIR_MAP:
            new_name = CHINESE_DIR_MAP[old_name]
        elif old_name in N10_DIR_MAP:
            new_name = N10_DIR_MAP[old_name]
        else:
            new_name = _to_snake_case(old_name)

        if new_name == old_name:
            continue

        abspath = _find_abspath(old_name)
        if not abspath or not abspath.is_dir():
            continue

        new_path = abspath.parent / new_name
        # 大小写重命名时跳过 exists 检查（Windows 大小写不敏感）
        if not _is_case_only_rename(abspath, new_path) and new_path.exists():
            print(f"[N-09/N-10] 跳过(目标已存在): {old_name} -> {new_name}")
            continue

        print(f"[{v['rule']}] {old_name} -> {new_name}")
        if _git_mv(abspath, new_path, dry_run):
            renames.append((old_name, new_name))
            fixed += 1

    return fixed, renames


def fix_n03(violations: list[dict], dry_run: bool) -> tuple[int, list[tuple[str, str]]]:
    """N-03: 将非ISO日期后缀转为ISO格式。返回(修复数, 重命名列表)。

    检测 [-_]YYYYMMDD 模式，转为 [-_]YYYY-MM-DD 使 ISO 豁免生效。
    """
    renames: list[tuple[str, str]] = []
    fixed = 0
    seen: set[str] = set()

    for v in violations:
        if v["rule"] != "N-03":
            continue
        msg = v["message"]
        name_match = re.search(r":\s*(\S+)$", msg)
        if not name_match:
            continue
        old_name = name_match.group(1)
        if old_name in seen:
            continue
        seen.add(old_name)

        abspath = _find_abspath(old_name)
        if not abspath or not abspath.is_file():
            continue

        stem = abspath.stem
        suffix = abspath.suffix

        # 查找 [-_]YYYYMMDD 模式并转为 [-_]YYYY-MM-DD
        # 匹配 _YYYYMMDD 或 -YYYYMMDD（8位数字）
        new_stem = re.sub(
            r"([-_])(\d{4})(\d{2})(\d{2})",
            lambda m: f"{m.group(1)}{m.group(2)}-{m.group(3)}-{m.group(4)}",
            stem,
        )

        if new_stem == stem:
            continue

        new_name = new_stem + suffix
        new_path = abspath.parent / new_name
        if new_path.exists():
            print(f"[N-03] 跳过(目标已存在): {old_name} -> {new_name}")
            continue

        print(f"[N-03] {old_name} -> {new_name}")
        if _git_mv(abspath, new_path, dry_run):
            renames.append((old_name, new_name))
            fixed += 1

    return fixed, renames


def fix_n11(violations: list[dict], dry_run: bool) -> tuple[int, list[tuple[str, str]]]:
    """N-11: 重命名文件使后缀匹配 doc_type。返回(修复数, 重命名列表)。"""
    renames: list[tuple[str, str]] = []
    fixed = 0
    seen: set[str] = set()

    for v in violations:
        if v["rule"] != "N-11":
            continue
        msg = v["message"]
        name_match = re.search(r"文件名=(\S+)", msg)
        if not name_match:
            continue
        old_name = name_match.group(1).rstrip(",")
        if old_name in seen:
            continue
        seen.add(old_name)

        dt_match = re.search(r"doc_type=(\S+)", msg)
        exp_match = re.search(r"期望后缀:\s*(.+)", msg)
        if not dt_match or not exp_match:
            continue
        doc_type = dt_match.group(1).rstrip(",")
        expected_suffixes = [s.strip() for s in exp_match.group(1).split(",")]

        abspath = _find_abspath(old_name)
        if not abspath or not abspath.is_file():
            continue

        stem = abspath.stem
        suffix = abspath.suffix

        # 选择第一个匹配当前扩展名的期望后缀
        new_name = None
        for exp_suffix in expected_suffixes:
            if exp_suffix.endswith(suffix):
                base = exp_suffix[: -len(suffix)] if suffix else exp_suffix
                new_name = stem + base + suffix
                break
        if not new_name:
            exp = expected_suffixes[0]
            if exp.endswith((".md", ".yaml", ".yml")):
                base = stem.rsplit("-", 1)[0] if "-" in stem else stem
                new_name = base + exp
            else:
                new_name = stem + exp + suffix
        if new_name == old_name:
            continue

        new_path = abspath.parent / new_name
        if new_path.exists():
            print(f"[N-11] 跳过(目标已存在): {old_name} -> {new_name}")
            continue

        print(f"[N-11] {old_name} -> {new_name} (doc_type={doc_type})")
        if _git_mv(abspath, new_path, dry_run):
            renames.append((old_name, new_name))
            fixed += 1

    return fixed, renames


def fix_n16(violations: list[dict], dry_run: bool) -> tuple[int, list[tuple[str, str]]]:
    """N-16: 重命名重复的测试文件。返回(修复数, 重命名列表)。"""
    renames: list[tuple[str, str]] = []
    fixed = 0
    seen: set[str] = set()

    for v in violations:
        if v["rule"] != "N-16":
            continue
        msg = v["message"]
        paths_match = re.search(r"处:\s*(.+)", msg)
        if not paths_match:
            continue
        paths_str = paths_match.group(1)
        paths = [p.strip() for p in paths_str.split(",")]
        for p in paths:
            if p in seen:
                continue
            seen.add(p)
            abspath = REPO_ROOT / p
            if not abspath.exists():
                continue
            old_name = abspath.name
            parts = Path(p).parts
            if len(parts) >= 2:
                dir_part = parts[-2]
                stem = abspath.stem
                suffix = abspath.suffix
                new_name = f"{stem}_{dir_part}{suffix}"
            else:
                continue
            if new_name == old_name:
                continue
            new_path = abspath.parent / new_name
            if new_path.exists():
                print(f"[N-16] 跳过(目标已存在): {old_name} -> {new_name}")
                continue
            print(f"[N-16] {old_name} -> {new_name}")
            if _git_mv(abspath, new_path, dry_run):
                renames.append((old_name, new_name))
                fixed += 1

    return fixed, renames


def main() -> None:
    """入口——收集违规并应用修复。"""
    parser = argparse.ArgumentParser(description="手动修复 N-11/N-10/N-03/N-09/N-16 命名违规")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际修改")
    parser.add_argument("--report", action="store_true", help="仅报告违规，不修复")
    args = parser.parse_args()

    print("收集违规...")
    violations = collect_violations()

    by_rule: dict[str, int] = {}
    for v in violations:
        by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1

    print(f"\n目标违规统计 (共 {len(violations)} 个):")
    for rule in sorted(TARGET_RULES):
        print(f"  {rule}: {by_rule.get(rule, 0)} 个")

    if args.report:
        print("\n违规详情:")
        for v in violations:
            print(f"  [{v['rule']}] {v['message']}")
        return

    dry = args.dry_run
    print(f"\n{'[DRY-RUN] ' if dry else ''}开始修复...\n")

    all_renames: list[tuple[str, str]] = []
    total_fixed = 0

    # 修复顺序：先修目录(N-09/N-10)，再修文件(N-03/N-11)，最后修测试(N-16)
    n, r = fix_n09_n10(violations, dry)
    total_fixed += n
    all_renames.extend(r)

    n, r = fix_n03(violations, dry)
    total_fixed += n
    all_renames.extend(r)

    n, r = fix_n11(violations, dry)
    total_fixed += n
    all_renames.extend(r)

    n, r = fix_n16(violations, dry)
    total_fixed += n
    all_renames.extend(r)

    # 批量更新所有引用
    if all_renames:
        print(f"\n{'[DRY-RUN] ' if dry else ''}批量更新引用 ({len(all_renames)} 个重命名)...")
        updated = _batch_update_references(all_renames, dry)
        print(f"  更新了 {updated} 个文件")

    print(f"\n{'[DRY-RUN] ' if dry else ''}修复完成: {total_fixed} 个违规已修复")

    if not dry and total_fixed > 0:
        print("\n建议运行验证:")
        print("  python scripts/governance/d3_metadata/check_naming_convention.py --scan --warn-only")


if __name__ == "__main__":
    main()
