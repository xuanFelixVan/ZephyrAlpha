# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/yaml_md/validate_yaml_summaries.py | §
# [MODULE] scripts.governance.d5_architecture.validators.yaml_md.validate_yaml_summaries
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.yaml_md.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""v1.0.0 -- 2026-05-03

GATE-A 代码↔YAML 对齐的根治层：
  根因：所有 YAML summary 字段（by_status / by_priority / by_maturity /
        by_quadrant / total_registered / global_stats）均为手动维护，
        无自动化交叉校验。每次数据变更后 summary 漂移不可避免。

  本闸门：自动扫描 architecture_model/ 下所有 YAML 文件，从实际条目数据
          反算聚合值 -> 与声明的 summary 逐项对比 -> 报告所有不一致。

检查范围：
  - layers/l*.yaml           -> modules[].status/priority/runtime_plane vs summary
  - infra/core_services.yaml -> services[].status/priority vs summary
  - infra/shared_infra.yaml  -> modules[].status/priority vs summary
  - scripts/scripts_model.yaml -> modules[].status/priority/runtime_plane vs summary
  - frontend/*.yaml           -> modules[].status/priority vs summary
  - cross-cutting/capability_heatmap.yaml -> capabilities[].current_level vs summary.by_maturity
  - technology/technology_landscape.yaml  -> technologies[].quadrant vs summary.by_quadrant
  - module_id_registry.yaml   -> registered_ids 条目数 vs total_registered
  - _index.yaml              -> partitions 条目数 vs global_stats.total_partitions
                              -> 跨文件聚合 P0/P1/P2/P3/deferred vs global_stats

对标：ITIL SACM -> CMDB 与实际基础设施定期对账（reconciliation）
     AWS Config -> 持续评估资源配置与期望状态的偏差
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-SUM - YAML Summary auto-reconciliation gate (scans all arch YAMLs, computes aggregation from actual data, compares with declared summary)
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()
ARCH_MODEL = REPO_ROOT / "architecture_model"
SCAN_ENTRIES = [
    ("layers", ARCH_MODEL / "layers", True),
    ("infra", ARCH_MODEL / "infra", True),
    ("scripts", ARCH_MODEL / "scripts", True),
    ("frontend", ARCH_MODEL / "frontend", True),
    ("cross-cutting", ARCH_MODEL / "cross-cutting", True),
    ("technology", ARCH_MODEL / "technology", True),
    ("data", ARCH_MODEL / "data", True),
    ("events", ARCH_MODEL / "events", True),
    ("domain", ARCH_MODEL / "domain", True),
]


def _count_by(items: list[dict], field: str) -> dict[str, int]:
    """_count_by implementation."""
    counts: dict[str, int] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        val = str(item.get(field, "")).strip()
        if not val:
            val = "(empty)"
        counts[val] = counts.get(val, 0) + 1
    return counts


def _check_count_dim(
    items: list[dict],
    item_field: str,
    summary: dict,
    summary_key: str,
    file_label: str,
    errors: list[str],
) -> None:
    """检查 summary 中某个分组维度（如 by_domain/by_frequency）与实际数据是否一致。

    若 summary 中不存在该维度键则跳过（返回 None），避免对无此维度的文件误报。
    """
    declared = summary.get(summary_key, {})
    if not isinstance(declared, dict) or not declared:
        return
    actual = _count_by(items, item_field)
    for key, declared_count in sorted(declared.items()):
        actual_count = actual.get(key, 0)
        if declared_count != actual_count:
            errors.append(f"{file_label}: summary.{summary_key}.{key}={declared_count}，实际={actual_count}")
    for key, actual_count in sorted(actual.items()):
        if key not in declared:
            errors.append(f"{file_label}: {item_field}={key} 存在 {actual_count} 个，summary.{summary_key} 未声明")


def validate_yaml_summaries() -> tuple[bool, list[str]]:
    """校验 YAML 摘要一致性"""
    errors: list[str] = []
    "校验 YAML 摘要一致性."
    for dir_label, dir_path, _ in SCAN_ENTRIES:
        if not dir_path.exists():
            continue
        for yaml_file in sorted(dir_path.glob("*.yaml")):
            if yaml_file.name in ("_schema.yaml",):
                continue
            data = load_yaml(yaml_file)
            if not data:
                continue
            items = None
            item_key = None
            for key in ("modules", "services", "capabilities", "technologies", "entities", "events"):
                candidate = data.get(key)
                if isinstance(candidate, list):
                    items = candidate
                    item_key = key
                    break
            if items is None:
                continue
            summary = data.get("summary", {})
            if not isinstance(summary, dict) or not summary:
                continue
            file_label = f"{dir_label}/{yaml_file.name}"
            actual_total = len(items)
            declared_total = (
                summary.get("total")
                or summary.get("total_technologies")
                or summary.get("total_capabilities")
                or summary.get("total_services")
                or summary.get("total_entities")
                or summary.get("total_events")
            )
            if declared_total is not None and declared_total != actual_total:
                errors.append(f"{file_label}: summary 声称 {declared_total} 个 {item_key}，实际 {actual_total} 个")
            declared_by_status = summary.get("by_status", {})
            if isinstance(declared_by_status, dict) and declared_by_status:
                actual = _count_by(items, "status")
                for status, declared in sorted(declared_by_status.items()):
                    actual_count = actual.get(status, 0)
                    if declared != actual_count:
                        errors.append(f"{file_label}: summary.by_status.{status}={declared}，实际={actual_count}")
                for status, actual_count in sorted(actual.items()):
                    if status not in declared_by_status:
                        errors.append(f"{file_label}: status={status} 存在 {actual_count} 个，summary.by_status 未声明")
            declared_by_priority = summary.get("by_priority", {})
            if isinstance(declared_by_priority, dict) and declared_by_priority:
                actual = _count_by(items, "priority")
                for priority, declared in sorted(declared_by_priority.items()):
                    actual_count = actual.get(priority, 0)
                    if declared != actual_count:
                        errors.append(f"{file_label}: summary.by_priority.{priority}={declared}，实际={actual_count}")
                for priority, actual_count in sorted(actual.items()):
                    if priority not in declared_by_priority:
                        errors.append(
                            f"{file_label}: priority={priority} 存在 {actual_count} 个，summary.by_priority 未声明"
                        )
            declared_by_plane = summary.get("by_runtime_plane", {})
            if isinstance(declared_by_plane, dict) and declared_by_plane:
                actual = _count_by(items, "runtime_plane")
                for plane, declared in sorted(declared_by_plane.items()):
                    actual_count = actual.get(plane, 0)
                    if declared != actual_count:
                        errors.append(f"{file_label}: summary.by_runtime_plane.{plane}={declared}，实际={actual_count}")
            declared_by_maturity = summary.get("by_maturity", {})
            if isinstance(declared_by_maturity, dict) and declared_by_maturity:
                actual: dict[str, int] = {}
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    val = item.get("maturity") or item.get("current_level")
                    if val is None:
                        val = "(empty)"
                    val = str(val).strip()
                    actual[val] = actual.get(val, 0) + 1
                for maturity, declared in sorted(declared_by_maturity.items()):
                    actual_count = actual.get(maturity, 0)
                    if declared != actual_count:
                        errors.append(f"{file_label}: summary.by_maturity.{maturity}={declared}，实际={actual_count}")
            declared_by_quadrant = summary.get("by_quadrant", {})
            if isinstance(declared_by_quadrant, dict) and declared_by_quadrant:
                actual = _count_by(items, "quadrant")
                for quadrant, declared in sorted(declared_by_quadrant.items()):
                    actual_count = actual.get(quadrant, 0)
                    if declared != actual_count:
                        errors.append(f"{file_label}: summary.by_quadrant.{quadrant}={declared}，实际={actual_count}")
            _check_count_dim(items, "domain", summary, "by_domain", file_label, errors)
            _check_count_dim(items, "frequency", summary, "by_frequency", file_label, errors)
            _check_count_dim(items, "audit_level", summary, "by_audit_level", file_label, errors)
    registry_path = ARCH_MODEL / "module_id_registry.yaml"
    if registry_path.exists():
        data = load_yaml(registry_path)
        if data:
            registered_ids = data.get("registered_ids", [])
            if isinstance(registered_ids, list):
                actual = len(registered_ids)
                declared = data.get("total_registered")
                if declared is not None and declared != actual:
                    errors.append(
                        f"module_id_registry.yaml: total_registered={declared}，实际 registered_ids 条目数={actual}"
                    )
    # contracts/consumer_registry.yaml —— 嵌套结构（contracts → registered_consumers），
    # 不适用通用扁平 list 校验，需专用块校验 total_contracts_registered /
    # total_consumer_entries / tier_distribution 三类聚合计数。
    # 治本（audit-02 第3轮复审 2026-08-02）：原 GATE-SUM 覆盖仅 data/events/domain 等
    # 扁平 list 目录，漏 contracts/，导致 consumer_registry summary 漂移无人拦截。
    consumer_registry_path = ARCH_MODEL / "contracts" / "consumer_registry.yaml"
    if consumer_registry_path.exists():
        data = load_yaml(consumer_registry_path)
        if data:
            contracts = data.get("consumers", [])
            if isinstance(contracts, list):
                summary = data.get("summary", {})
                if isinstance(summary, dict) and summary:
                    actual_contracts = len(contracts)
                    declared_contracts = summary.get("total_contracts_registered")
                    if declared_contracts is not None and declared_contracts != actual_contracts:
                        errors.append(
                            f"contracts/consumer_registry.yaml: summary.total_contracts_registered={declared_contracts}，实际契约数={actual_contracts}"
                        )
                    registered_lists = [c.get("registered_consumers", []) for c in contracts if isinstance(c, dict)]
                    actual_entries = sum(len(r) for r in registered_lists if isinstance(r, list))
                    declared_entries = summary.get("total_consumer_entries")
                    if declared_entries is not None and declared_entries != actual_entries:
                        errors.append(
                            f"contracts/consumer_registry.yaml: summary.total_consumer_entries={declared_entries}，实际消费者条目数={actual_entries}"
                        )
                    tier_dist = summary.get("tier_distribution", {})
                    if isinstance(tier_dist, dict) and tier_dist:
                        actual_tier: dict[str, int] = {}
                        for r_list in registered_lists:
                            if not isinstance(r_list, list):
                                continue
                            for r in r_list:
                                if not isinstance(r, dict):
                                    continue
                                tval = str(r.get("tier", "")).strip()
                                if not tval:
                                    tval = "(empty)"
                                actual_tier[tval] = actual_tier.get(tval, 0) + 1
                        for skey, declared_count in tier_dist.items():
                            if not isinstance(skey, str) or not skey.startswith("tier_"):
                                continue
                            parts = skey.split("_")
                            if len(parts) < 2 or not parts[1].isdigit():
                                continue
                            tval = parts[1]
                            actual_count = actual_tier.get(tval, 0)
                            if declared_count != actual_count:
                                errors.append(
                                    f"contracts/consumer_registry.yaml: summary.tier_distribution.{skey}={declared_count}，实际 tier={tval} 共 {actual_count} 个"
                                )
    index_path = ARCH_MODEL / "index.yaml"
    if index_path.exists():
        data = load_yaml(index_path)
        if data:
            global_stats = data.get("global_stats", {})
            partitions = data.get("partitions", [])
            if isinstance(global_stats, dict):
                declared = global_stats.get("total_partitions")
                if declared is not None:
                    actual = len(partitions) if isinstance(partitions, list) else 0
                    if declared != actual:
                        errors.append(
                            f"index.yaml: global_stats.total_partitions={declared}，实际 partitions 条目数={actual}"
                        )
                cross_p0 = 0
                cross_p1 = 0
                cross_p2 = 0
                cross_p3 = 0
                cross_deferred = 0
                all_items: list[dict] = []
                for dir_label, dir_path, _ in SCAN_ENTRIES:
                    if not dir_path.exists():
                        continue
                    for yaml_file in sorted(dir_path.glob("*.yaml")):
                        if yaml_file.name in ("_schema.yaml",):
                            continue
                        d = load_yaml(yaml_file)
                        if not d:
                            continue
                        items = None
                        for key in ("modules", "services"):
                            candidate = d.get(key)
                            if isinstance(candidate, list):
                                items = candidate
                                break
                        if not items:
                            continue
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            all_items.append(item)
                            p = (item.get("priority") or "").strip().upper()
                            s = (item.get("status") or "").strip().lower()
                            if p == "P0":
                                cross_p0 += 1
                            elif p == "P1":
                                cross_p1 += 1
                            elif p == "P2":
                                cross_p2 += 1
                            elif p == "P3":
                                cross_p3 += 1
                            if s == "deferred":
                                cross_deferred += 1

                def _check_global(field: str, declared_val, actual_val: int):
                    """_check_global implementation."""
                    if declared_val is not None and declared_val != actual_val:
                        errors.append(f"index.yaml: global_stats.{field}={declared_val}，实际跨文件聚合={actual_val}")

                total_all = len(all_items)
                _check_global("total_modules_p0", global_stats.get("total_modules_p0"), cross_p0)
                _check_global("total_modules_p1", global_stats.get("total_modules_p1"), cross_p1)
                _check_global("total_modules_p2", global_stats.get("total_modules_p2"), cross_p2)
                _check_global("total_modules_p3", global_stats.get("total_modules_p3"), cross_p3)
                _check_global("total_modules_deferred", global_stats.get("total_modules_deferred"), cross_deferred)
    return (len(errors) == 0, errors)


def main() -> None:
    """入口函数."""
    import argparse

    parser = argparse.ArgumentParser(description="YAML Summary 自动对账闸门（GATE-SUM）——根治 summary 手动维护漂移")
    parser.add_argument("--warn-only", action="store_true", help="仅报告不阻断")
    args = parser.parse_args()
    print("=" * 60)
    print("GATE-SUM: YAML Summary 自动对账 v1.0.0")
    print("=" * 60)
    passed, errors = validate_yaml_summaries()
    if not errors:
        print("\n✅ 所有 YAML summary 字段与实际数据完全一致——零漂移")
        return EXIT_PASS
    print(f"\n🔍 发现 {len(errors)} 项 summary 漂移：\n")
    for i, e in enumerate(errors, 1):
        print(f"  [{i:02d}] {e}")
    if args.warn_only:
        print(f"\n⚠️  --warn-only 模式：{len(errors)} 项漂移仅告警，不阻断")
        return EXIT_PASS
    else:
        print(f"\n⛔ {len(errors)} 项 summary 漂移——阻断！")
        print("   修复方法：根据实际数据条目逐项更新对应 YAML 的 summary 字段")
        print("   或运行：python scripts/governance/d5_architecture/validate_yaml_summaries.py --warn-only")
        return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
