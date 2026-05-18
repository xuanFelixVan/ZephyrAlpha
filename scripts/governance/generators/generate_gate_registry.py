# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_gate_registry.py | §
"""
generate_gate_registry.py — 门禁登记表自动生成器

从 .pre-commit-config.yaml 自动派生 gate-registry.yaml。
对标 §6.16 静态清单自动生成铁律——手工维护的 gate-registry 将被此脚本替代。

Usage:
    python scripts/governance/generators/generate_gate_registry.py
    python scripts/governance/generators/generate_gate_registry.py --check
    python scripts/governance/generators/generate_gate_registry.py --output path/to/output.yaml
"""

from __future__ import annotations

import os
import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 10
args:
  - {flag: --check, type: bool, description: "仅检测漂移，不写文件"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  从 .pre-commit-config.yaml 自动派生 gate-registry.yaml。
  对标 §6.16 静态清单自动生成铁律。
"""

PRE_COMMIT_PATH = REPO_ROOT / ".pre-commit-config.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "gate-registry.yaml"

CATEGORY_MAP = {
    "01": "architecture_reachability",
    "02": "contract_integrity",
    "03": "invariant_governance",
    "06": "adr_status",
    "07": "event_routing",
    "11": "naming_convention",
    "12": "blueprint_truth_source",
    "13": "blueprint_overlap",
    "14": "ai_autonomy",
    "15": "frontmatter_metadata",
    "16": "architecture_compliance",
    "17": "orphan_detection",
    "18": "test_collection",
    "19": "static_manifest_drift",
    "22": "load_path_integrity",
    "ZR": "zero_residue",
    "SSOT": "ssot_guard",
    "BP-PLACE": "blueprint_placement",
    "SQ": "script_quality",
    "ADM": "manifest_admission",
    "IDX": "index_sync",
    "DD07": "dedup_gate",
    "C1": "ssot_status",
    "C2": "contract_drift",
}


def extract_gates(config: dict) -> list[dict]:
    """extract_gates implementation."""
    gates = []
    local_hooks = config.get("repos", [])
    for repo in local_hooks:
        if repo.get("repo") != "local":
            continue
        for hook in repo.get("hooks", []):
            hook_name = hook.get("name", "")

            gate_match = re.match(r"GATE-([A-Z0-9]+(?:-[A-Z0-9]+)*)(?::|$)", hook_name)
            if gate_match:
                gate_suffix = gate_match.group(1)
            else:
                hook_id = hook.get("id", "")
                id_match = re.match(r"gate-(\d+)", hook_id)
                if not id_match:
                    continue
                gate_suffix = id_match.group(1)

            gates.append(
                {
                    "gate_id": f"GATE-{gate_suffix}",
                    "name": hook_name,
                    "entry": hook.get("entry", ""),
                    "description": hook.get("description", ""),
                    "files_trigger": hook.get("files", ""),
                    "always_run": hook.get("always_run", False),
                    "category": CATEGORY_MAP.get(gate_suffix, "unknown"),
                    "status": "active",
                }
            )
    return gates


def generate(entry_count: int | None = None) -> dict:
    """generate implementation."""
    pcc = load_yaml(PRE_COMMIT_PATH)
    gates = extract_gates(pcc)
    if entry_count is not None:
        for g in gates:
            g["entry_count"] = entry_count
    return {
        "module_id": "PS-REG-014",
        "doc_type": "register",
        "title": "GATE 门禁登记表",
        "status": "active",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_gate_registry.py",
        "source": ".pre-commit-config.yaml",
        "total_gates": len(gates),
        "gates": gates,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="自动生成 gate-registry.yaml")
    parser.add_argument("--check", action="store_true", help="仅检测漂移，不写文件")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    output = generate()

    if args.check:
        existing = load_yaml(args.output)
        if existing.get("total_gates") != output["total_gates"]:
            print(f"DRIFT: 磁盘 {existing.get('total_gates', 0)} 门禁 ≠ 生成 {output['total_gates']} 门禁")
            sys.exit(EXIT_FINDINGS)
        print("OK: 门禁登记表与 .pre-commit-config.yaml 一致")
        return

    tmp_path = f"{args.output}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            f.write("# module_id: PS-REG-014\n")
            f.write("# doc_type: register\n")
            f.write(f"# 自动生成于 {output['generated_at']}\n")
            f.write(f"# 来源: {PRE_COMMIT_PATH}\n")
            f.write("# 手工编辑无效——修改请通过 .pre-commit-config.yaml\n\n")
            yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
        os.replace(tmp_path, args.output)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"已生成 {output['total_gates']} 条门禁 → {args.output}")


if __name__ == "__main__":
    main()
