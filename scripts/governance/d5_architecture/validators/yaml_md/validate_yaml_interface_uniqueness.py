# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/yaml_md/validate_yaml_interface_uniqueness.py | §
# [MODULE] scripts.governance.d5_architecture.validators.yaml_md.validate_yaml_interface_uniqueness
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.yaml_md.__init__
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
#!/usr/bin/env python3
"""validate_yaml_interface_uniqueness.py — YAML 模块接口唯一性闸门（GATE-IFACE-UNIQ）
v1.0.0 — 2026-05-03



根因（R6 审计 P0-09）：AI session 编写层 YAML 时，对同一 contract_id 同时添加
consumer 和 producer 两条记录，应合并为 role: both。此模式在 l00/l04/l06/l12
中各出现 1-2 次，属于 AI 上下文窗口有限导致的重复写入。

本闸门：扫描所有分区 YAML，检测同一模块内 contract_id 重复条目，
        报告应合并为 role: both 的冲突。

检查维度：
  DIM-1: 同一模块内 contract_id 重复 → 建议合并为 role: both
  DIM-2: 同一模块内 contract_id + role 完全相同 → 完全重复（应删除）

对标：OpenAPI path uniqueness / K8s CRD field name uniqueness

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: YAML 接口唯一性校验（防止同一接口在多处重复定义）
dimensions:
- D3
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

ARCH_MODEL = REPO_ROOT / "architecture_model"


def scan_partition_yaml(yaml_path: Path) -> list[dict]:
    """扫描 YAML 接口唯一性."""
    findings = []
    """扫描并返回发现列表."""
    data = load_yaml(yaml_path)
    if not data:
        return findings

    modules = data.get("modules", [])
    if not modules:
        return findings

    for mod in modules:
        mod_id = mod.get("id", "?")
        interfaces = mod.get("interfaces", [])
        if not interfaces:
            continue

        cid_count = Counter(iface.get("contract_id", "") for iface in interfaces)
        for cid, count in cid_count.items():
            if not cid or count <= 1:
                continue

            roles = set()
            for iface in interfaces:
                if iface.get("contract_id") == cid:
                    roles.add(iface.get("role", "?"))

            if len(roles) > 1:
                findings.append(
                    {
                        "type": "MERGE_TO_BOTH",
                        "module": mod_id,
                        "contract_id": cid,
                        "roles": sorted(roles),
                        "suggestion": "合并为 role: both",
                    }
                )
            else:
                findings.append(
                    {
                        "type": "EXACT_DUPLICATE",
                        "module": mod_id,
                        "contract_id": cid,
                        "roles": sorted(roles),
                        "suggestion": "删除重复条目（保留一条即可）",
                    }
                )

    return findings
    """扫描 YAML 接口唯一性."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-IFACE-UNIQ: YAML 模块接口唯一性闸门 v1.0.0")
    print("=" * 72)

    all_findings = []
    yaml_files = list(ARCH_MODEL.rglob("*.yaml"))
    yaml_files = [f for f in yaml_files if f.name != "_schema.yaml"]

    for fpath in sorted(yaml_files):
        rel = fpath.relative_to(ARCH_MODEL)
        findings = scan_partition_yaml(fpath)
        for f in findings:
            f["file"] = str(rel)
        all_findings.extend(findings)

    if not all_findings:
        print("\n✅ 所有模块接口唯一——零重复")
        return EXIT_PASS
    print(f"\n🔴 发现 {len(all_findings)} 个接口唯一性问题：\n")
    for f in all_findings:
        icon = "⚠️" if f["type"] == "MERGE_TO_BOTH" else "🔴"
        print(
            f"  {icon} {f['file']}: {f['module']} → {f['contract_id']} "
            f"(roles: {', '.join(f['roles'])}) → {f['suggestion']}"
        )

    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
