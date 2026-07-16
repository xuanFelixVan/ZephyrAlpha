# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_code_yaml_alignment.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_code_yaml_alignment
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] permanent
"""validate_code_yaml_alignment.py — GATE-A: 实际代码 ↔ YAML SSoT 对账



对标：GATE-A 代码↔YAML 对齐
      YAML canonical SSoT 铁律

检测内容：
- CRITICAL: 实际存在的代码目录未在 architecture_model/ YAML 中登记
- HIGH: YAML 登记的文件在实际磁盘上不存在
- MEDIUM: YAML 登记的模块文件数与实际文件数不一致

exit codes: 0=对齐, 1=发现漂移, 2=脚本错误
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-A — 实际代码目录↔architecture_model/YAML SSoT 对账，检测未登记目录/YAML漂移/文件数不一致
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

import yaml


def _load_yaml(path: Path) -> dict:
    """_load_yaml implementation."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _list_top_dirs(code_dir: Path) -> dict[str, Path]:
    """_list_top_dirs implementation."""
    dirs: dict[str, Path] = {}
    for p in sorted(code_dir.iterdir()):
        if not p.is_dir():
            continue
        if p.name in EXCLUDE_DIRS or p.name.startswith(".") or p.name.startswith("__"):
            continue
        dirs[p.name] = p
    return dirs


def _collect_actual_files(dir_path: Path) -> frozenset[str]:
    """_collect_actual_files implementation."""
    files: set[str] = set()
    for p in dir_path.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".yaml", ".yml"):
            files.add(p.name)
    return frozenset(files)


def _parse_index(index_path: Path) -> dict:
    """_parse_index implementation.

    v3.0.2 单树结构：partitions 是列表，b_track partition 的 modules 子列表
    每个模块的 path 指向 layers/b_*.yaml。c_track 已删除（14层降级为域属性）。
    """
    index = _load_yaml(index_path)
    yaml_dir = index_path.parent

    partitions: dict[str, dict] = {}
    for part in index.get("partitions", []):
        pid = part.get("id", "")
        # b_track partition: 从 modules 列表提取每个模块的 layer_path
        if pid == "b_track" and "modules" in part:
            for mod in part["modules"]:
                mod_id = mod["id"]
                layer_rel = mod.get("path", "")
                layer_path = yaml_dir / layer_rel
                partitions[mod_id] = {
                    "track": "b",
                    "layer_path": layer_path,
                    "index_status": mod.get("status", "unknown"),
                }
    return partitions


def scan_alignment(code_dir: Path, yaml_dir: Path) -> tuple[list[str], list[str], list[str], int, int]:
    """扫描代码-YAML 对齐一致性."""
    criticals: list[str] = []
    """扫描并返回发现列表."""
    highs: list[str] = []
    mediums: list[str] = []

    index_path = yaml_dir / "index.yaml"
    if not index_path.exists():
        criticals.append(f"index.yaml 不存在: {index_path}")
        return criticals, highs, mediums, 0, 0

    yaml_partitions = _parse_index(index_path)
    actual_dirs = _list_top_dirs(code_dir)

    total = 0
    aligned = 0

    # CRITICAL: 实际存在但 YAML 未登记的目录
    yaml_expected_dirs: set[str] = set()
    for pid, info in yaml_partitions.items():
        # b_track: pid 即模块名，目录名与 pid 一致（c_track 已删除）
        yaml_expected_dirs.add(pid)

    for dir_name in sorted(actual_dirs):
        if dir_name not in yaml_expected_dirs:
            criticals.append(
                f"目录存在但 YAML 未登记: src/zephyr/{dir_name}/ "
                f"— GATE-A 违规，请在 architecture_model/index.yaml 添加"
            )

    # HIGH/MEDIUM: YAML ↔ 实际文件对账
    for pid, info in sorted(yaml_partitions.items()):
        total += 1
        lp = info["layer_path"]
        if not lp.exists():
            highs.append(f"{pid}: 层 YAML 文件不存在: {lp.relative_to(REPO_ROOT)}")
            continue

        ly = _load_yaml(lp)
        # b_track: expected_dir 与 pid 一致（c_track 已删除）
        expected_dir = pid

        if expected_dir not in actual_dirs:
            if ly.get("partition", {}).get("status") == "skeleton":
                continue
            criticals.append(f"{pid}: YAML 已登记(implemented)但目录不存在: src/zephyr/{expected_dir}/")
            continue

        dir_path = actual_dirs[expected_dir]
        actual_files = _collect_actual_files(dir_path)
        module_ok = True

        yaml_files: set[str] = set()
        for mod in ly.get("modules", []):
            for f in mod.get("files", []):
                yaml_files.add(f)
            for f in mod.get("components", []):
                yaml_files.add(f)

        for f in sorted(yaml_files - actual_files):
            highs.append(f"{pid}: YAML 登记 '{f}' 但磁盘不存在 — 请更新 YAML 或创建文件")
            module_ok = False

        for f in sorted(actual_files - yaml_files):
            if f == "__init__.py":
                continue
            mediums.append(f"{pid}: 磁盘有 '{f}' 但 YAML 未登记 — 请更新 {lp.name}")
            module_ok = False

        summary = ly.get("summary", {})
        yaml_count = summary.get("total", 0)
        actual_count = len(ly.get("modules", []))
        if yaml_count != actual_count:
            mediums.append(f"{pid}: YAML summary.total={yaml_count} ≠ modules数量={actual_count}")

        if module_ok:
            aligned += 1

    return criticals, highs, mediums, total, aligned
    """扫描代码-YAML 对齐一致性."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="GATE-A: src/zephyr/ ↔ architecture_model/ 双层对账")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="诊断模式：发现漂移不阻断",
    )
    parser.add_argument(
        "--code-dir",
        type=str,
        default=str(REPO_ROOT / "src" / "zephyr"),
        help="源代码目录",
    )
    parser.add_argument(
        "--yaml-dir",
        type=str,
        default=str(REPO_ROOT / "architecture_model"),
        help="YAML SSoT 目录",
    )
    args = parser.parse_args()

    code_dir = Path(args.code_dir)
    yaml_dir = Path(args.yaml_dir)

    for d, label in [(code_dir, "代码"), (yaml_dir, "YAML")]:
        if not d.exists():
            print(f"[ERROR] {label}目录不存在: {d}", file=sys.stderr)
            sys.exit(EXIT_ERROR)

    criticals, highs, mediums, total, aligned = scan_alignment(code_dir, yaml_dir)

    print(f"\n[GATE-A] 代码↔YAML 双层对齐闸门 — {total} 模块\n")

    has_issues = bool(criticals or highs or mediums)

    if criticals:
        print(f"🔴 CRITICAL ({len(criticals)}):")
        for c in criticals:
            print(f"  {c}")
        print()

    if highs:
        print(f"🟠 HIGH ({len(highs)}):")
        for h in highs:
            print(f"  {h}")
        print()

    if mediums:
        print(f"🟡 MEDIUM ({len(mediums)}):")
        for m in mediums:
            print(f"  {m}")
        print()

    if not has_issues:
        print(f"✅ 全部对齐 — {aligned}/{total} 模块通过 GATE-A\n")

    print(f"  总计: {total} 模块, {len(criticals)} CRITICAL, {len(highs)} HIGH, {len(mediums)} MEDIUM\n")

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if criticals or highs else EXIT_PASS)


if __name__ == "__main__":
    main()
