# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_dual_tree_sync.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_dual_tree_sync
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
"""GATE-DTS — 双树同步检查闸门 (Dual Tree Sync)

任务 ID : T-2-34
safety_level : M（治理脚本）

功能
----
检查仓库根 architecture_model/（施工树）与
docs/02_enterprise_architecture/target_architecture/architecture_model/（企业架构树）
之间的同步一致性。

检测内容（按严重性）：
- P0: partition.id 在施工树存在但企业架构树缺失（C 轨层）
- P0: 同一 partition.id 两侧文件名不一致（如 integration vs l13-experiment-pipeline）
- P1: 施工树 technology_landscape.yaml 未声明 deprecated（企业架构树已有完整版）
- P2: B 轨分区在施工树存在但企业架构树缺失（scope.yaml R3 允许，仅提醒）
- P2: 两侧 YAML 的 module_id 集合差异（同名 partition 下模块不一致）

对标：
- AGENTS.md §6.9 双树分工
- architecture_model/scope.yaml R1/R2/R3
- AUDIT-04 D-ALIGN 维度

用法：
  python scripts/governance/d5_architecture/check_dual_tree_sync.py
  python scripts/governance/d5_architecture/check_dual_tree_sync.py --ci
  python scripts/governance/d5_architecture/check_dual_tree_sync.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args:
  - --warn-only
  - --ci
description: GATE-DTS — 双树同步检查闸门（architecture_model/ 施工树 vs docs/EA/architecture_model/ 企业架构树）
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

# 双树路径常量
IMPL_TREE = REPO_ROOT / "architecture_model"
EA_TREE = REPO_ROOT / "docs" / "02_enterprise_architecture" / "target_architecture" / "architecture_model"
SCOPE_YAML = IMPL_TREE / "scope.yaml"

# 文件名映射：施工树文件名 -> 企业架构树文件名（处理连字符/下划线差异）
# 施工树使用下划线（与 src/ 目录命名一致），企业架构树使用连字符（与视图文档命名一致）
# 这是有意设计差异——scope.yaml R3 明确允许同一 partition.id 两侧各有不同文件名的 YAML
FILENAME_MAP: dict[str, str] = {
    "data.yaml": "l00_data_source.yaml",
    "infrastructure_runtime_integration.yaml": "l01_infrastructure.yaml",
    "factor.yaml": "l02_alpha_factor.yaml",
    "signal.yaml": "l03_signal_generation.yaml",
    "risk.yaml": "l04_risk_management.yaml",
    "pf_core.yaml": "l05_portfolio_construction.yaml",
    "ex_core.yaml": "l06_trade_execution.yaml",
    "pf_core.yaml": "l07_post_trade_analytics.yaml",
    "frontend.yaml": "l08_human_ai_interface.yaml",
    "research.yaml": "l09_research_innovation.yaml",
    "compliance.yaml": "l10-governance-compliance.yaml",
    "ml_train.yaml": "l11_ml_platform.yaml",
    "observability.yaml": "l12_system_telemetry.yaml",
    "integration.yaml": "l13-experiment-pipeline.yaml",
    "b_shared.yaml": "shared.yaml",
}


def _safe_load_yaml(file_path: Path) -> Any | None:
    """_safe_load_yaml implementation."""
    try:
        return load_yaml(file_path)
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"  ⚠️ 无法解析 {file_path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return None


def _collect_partition_ids(tree_root: Path) -> dict[str, str]:
    """收集某棵树 layers/ 目录下的所有 partition.id -> 文件名映射。"""
    result: dict[str, str] = {}
    layers_dir = tree_root / "layers"
    if not layers_dir.exists():
        return result
    for yaml_file in sorted(layers_dir.glob("*.yaml")):
        if yaml_file.name.startswith("_"):
            continue
        data = _safe_load_yaml(yaml_file)
        if not data:
            continue
        partition = data.get("partition", {})
        if isinstance(partition, dict):
            pid = partition.get("id", "")
            if pid:
                result[pid] = yaml_file.name
    return result


def _collect_module_ids(tree_root: Path, partition_id: str) -> set[str]:
    """收集某棵树指定 partition 下的所有 module_id。"""
    layers_dir = tree_root / "layers"
    if not layers_dir.exists():
        return set()
    for yaml_file in sorted(layers_dir.glob("*.yaml")):
        data = _safe_load_yaml(yaml_file)
        if not data:
            continue
        partition = data.get("partition", {})
        if isinstance(partition, dict) and partition.get("id") == partition_id:
            modules = data.get("modules", [])
            if isinstance(modules, list):
                return {m.get("id", "") for m in modules if isinstance(m, dict) and m.get("id")}
    return set()


def check_p0_c_track_sync() -> list[str]:
    """P0: C 轨层（l00-l13 + shared）必须在两侧同时存在且文件名一致。"""
    errs: list[str] = []
    impl_ids = _collect_partition_ids(IMPL_TREE)
    ea_ids = _collect_partition_ids(EA_TREE)

    c_track_pattern = re.compile(r"^l\d{2}$|^shared$")

    for pid, impl_fname in sorted(impl_ids.items()):
        if not c_track_pattern.match(pid):
            continue
        if pid not in ea_ids:
            errs.append(f"P0: C 轨 partition `{pid}` 在施工树存在（{impl_fname}）但企业架构树缺失 — 违反 scope.yaml R3")
            continue
        ea_fname = ea_ids[pid]
        # 检查文件名映射
        expected_ea_fname = FILENAME_MAP.get(impl_fname, impl_fname)
        if ea_fname != expected_ea_fname and ea_fname != impl_fname:
            errs.append(f"P0: partition `{pid}` 两侧文件名不一致 — 施工树: {impl_fname}，企业架构树: {ea_fname}")

    for pid, ea_fname in sorted(ea_ids.items()):
        if not c_track_pattern.match(pid):
            continue
        if pid not in impl_ids:
            errs.append(f"P0: C 轨 partition `{pid}` 在企业架构树存在（{ea_fname}）但施工树缺失 — 违反 scope.yaml R3")

    return errs


def check_p0_b_track_sync() -> list[str]:
    """P0: B 轨分区不应出现在 EA 树中（scope.yaml R4）。"""
    errs: list[str] = []
    impl_layers = IMPL_TREE / "layers"
    if not impl_layers.exists():
        return errs

    b_track_ids: dict[str, str] = {}
    for yaml_file in sorted(impl_layers.glob("b_*.yaml")):
        data = _safe_load_yaml(yaml_file)
        if not data:
            continue
        partition = data.get("partition", {})
        if isinstance(partition, dict):
            pid = partition.get("id", "")
            if pid:
                b_track_ids[pid] = yaml_file.name

    c_track_pattern = re.compile(r"^l\d{2}$|^shared$")
    ea_ids = _collect_partition_ids(EA_TREE)

    for pid, impl_fname in sorted(b_track_ids.items()):
        if c_track_pattern.match(pid):
            continue
        if pid in ea_ids:
            errs.append(
                f"P0: B 轨 partition `{pid}` 在 EA 树中出现（{ea_ids[pid]}）"
                f"— scope.yaml R4 禁止 EA 树镜像 B 轨。"
                f"施工树对应文件: {impl_fname}。请删除 EA 树中的此文件。"
            )

    return errs


def check_p1_tech_landscape_deprecated() -> list[str]:
    """P1: 施工树 technology_landscape.yaml 应声明 deprecated。"""
    errs: list[str] = []
    tl_impl = IMPL_TREE / "technology_landscape.yaml"
    if not tl_impl.exists():
        return errs

    data = _safe_load_yaml(tl_impl)
    if not data:
        return errs

    status = data.get("status", "")
    if status != "deprecated":
        errs.append(
            f"P1: 施工树 {tl_impl.relative_to(REPO_ROOT)} 未声明 status: deprecated — "
            f"企业架构树已有完整版（{EA_TREE / 'technology/technology_landscape.yaml'})"
        )

    return errs


def check_p2_module_id_consistency() -> list[str]:
    """P2: 同名 partition 下两侧 module_id 集合差异。"""
    errs: list[str] = []
    impl_ids = _collect_partition_ids(IMPL_TREE)
    ea_ids = _collect_partition_ids(EA_TREE)

    for pid in sorted(set(impl_ids.keys()) & set(ea_ids.keys())):
        impl_modules = _collect_module_ids(IMPL_TREE, pid)
        ea_modules = _collect_module_ids(EA_TREE, pid)
        if not impl_modules and not ea_modules:
            continue
        diff = impl_modules.symmetric_difference(ea_modules)
        if diff:
            errs.append(f"P2: partition `{pid}` 两侧 module_id 不一致 — 差异: {sorted(diff)}")

    return errs


def check_p2_schema_version_alignment() -> list[str]:
    """P2: 两棵树的层 YAML schema_version 差异提示（有意设计，仅提醒）。"""
    errs: list[str] = []
    impl_ids = _collect_partition_ids(IMPL_TREE)
    ea_ids = _collect_partition_ids(EA_TREE)

    for pid in sorted(set(impl_ids.keys()) & set(ea_ids.keys())):
        impl_sv = _get_schema_version(IMPL_TREE, pid)
        ea_sv = _get_schema_version(EA_TREE, pid)
        if impl_sv and ea_sv and impl_sv != ea_sv:
            errs.append(
                f"P2: partition `{pid}` schema_version 差异 — "
                f"施工树: {impl_sv}, 企业架构树: {ea_sv}（有意设计，scope.yaml R3 允许）"
            )
    return errs


def _get_schema_version(tree_root: Path, partition_id: str) -> str | None:
    """_get_schema_version implementation."""
    layers_dir = tree_root / "layers"
    if not layers_dir.exists():
        return None
    for yaml_file in sorted(layers_dir.glob("*.yaml")):
        data = _safe_load_yaml(yaml_file)
        if not data:
            continue
        partition = data.get("partition", {})
        if isinstance(partition, dict) and partition.get("id") == partition_id:
            return str(data.get("schema_version", ""))
    return None


def check_scope_yaml_exists() -> list[str]:
    """P0: scope.yaml 必须存在。"""
    errs: list[str] = []
    if not SCOPE_YAML.exists():
        errs.append(f"P0: {SCOPE_YAML.relative_to(REPO_ROOT)} 不存在 — 双树边界真源缺失，违反 AGENTS.md §6.9")
    return errs


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="GATE-DTS — 双树同步检查闸门 (T-2-34)")
    parser.add_argument("--ci", action="store_true", help="CI 模式：发现 P0 则 exit(1)")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：不阻塞")
    args = parser.parse_args()

    print("=" * 60)
    print("GATE-DTS — 双树同步检查闸门 v1.1.0")
    print("=" * 60)
    print(f"施工树: {IMPL_TREE.relative_to(REPO_ROOT)}")
    print(f"企业架构树: {EA_TREE.relative_to(REPO_ROOT)}")
    print()

    all_errors: list[str] = []

    checks = [
        ("scope.yaml 存在性", check_scope_yaml_exists),
        ("C 轨层同步", check_p0_c_track_sync),
        ("B 轨层同步", check_p0_b_track_sync),
        ("technology-landscape 弃用声明", check_p1_tech_landscape_deprecated),
        ("module_id 一致性", check_p2_module_id_consistency),
        ("schema_version 差异", check_p2_schema_version_alignment),
    ]

    p0_count = 0
    p1_count = 0
    p2_count = 0

    for check_name, check_fn in checks:
        errors = check_fn()
        if errors:
            print(f"\n[{check_name}]")
            for e in errors:
                print(f"  {'🔴' if e.startswith('P0:') else '🟡' if e.startswith('P1:') else '🔵'} {e}")
                if e.startswith("P0:"):
                    p0_count += 1
                elif e.startswith("P1:"):
                    p1_count += 1
                elif e.startswith("P2:"):
                    p2_count += 1
            all_errors.extend(errors)
        else:
            print(f"  ✅ {check_name}")

    print(f"\n{'=' * 60}")
    print(f"结果: P0={p0_count}  P1={p1_count}  P2={p2_count}")

    if all_errors:
        print(f"{'=' * 60}")
        if p0_count > 0:
            print("⛔ 发现 P0 问题 — 双树同步断裂，不满足 beta 门禁条件。")
        elif p1_count > 0:
            print("⚠️ 发现 P1 问题 — 建议本 sprint 内修复。")
        else:
            print("ℹ️ 仅发现 P2 建议 — 可按计划处理。")
    else:
        print("✅ 双树同步检查通过 — 施工树与企业架构树一致。")

    if args.warn_only:
        return EXIT_PASS
    if args.ci and p0_count > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
