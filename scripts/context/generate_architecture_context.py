"""
generate_architecture_context.py — 预编译架构上下文包生成器

从 SSoT YAML + ADR + 治理文档中提取关键架构信息，压缩为 AI 可直接消费的
JSON 上下文包。解决 "每个 AI session 重新学习架构" 的问题。

输出: src/zephyr/context_engine/architecture_context.json

用法: python scripts/context/generate_architecture_context.py
      python scripts/context/generate_architecture_context.py --watch  # 文件变更自动重生成

SSoT: cross-layer-contracts.yaml + ADR index + governance structure
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parents[1] / ""

if not REPO_ROOT.exists():
    REPO_ROOT = Path.cwd()

import yaml

CONTRACTS_YAML = REPO_ROOT / (
    "docs/02_enterprise_architecture/target-architecture/" "architecture-model/contracts/cross-layer-contracts.yaml"
)
ADR_DIR = REPO_ROOT / "docs/02_enterprise_architecture/adr"
OUTPUT_PATH = REPO_ROOT / "src/zephyr/context_engine/architecture_context.json"

LAYER_NAMES = {
    "l00": "数据源层",
    "l01": "基础设施层",
    "l02": "Alpha 因子层",
    "l03": "信号生成层",
    "l04": "风险管理层",
    "l05": "组合构建层",
    "l06": "交易执行层",
    "l07": "后交易分析层",
    "l08": "人机交互层",
    "l09": "研究创新层",
    "l10": "合规层",
    "l11": "ML 平台层",
    "l12": "系统遥测层",
    "l13": "实验层",
}


def main() -> None:
    context = {
        "generated_at": datetime.now(UTC).isoformat(),
        "version": "3.0",
        "schema": "zephyr-alpha-architecture-context/v1",
    }

    _extract_contracts_summary(context)
    _extract_layer_summary(context)
    _extract_adr_summary(context)
    _extract_governance_rules(context)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[ArchContext] 预编译架构上下文已生成 → {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  - P0 契约: {len(context.get('contracts', {}).get('p0', []))} 条")
    print(f"  - P1 契约: {len(context.get('contracts', {}).get('p1', []))} 条")
    print(f"  - 层定义: {len(context.get('layers', []))} 层")
    print(f"  - ADR: {len(context.get('adrs', []))} 份")


def _extract_contracts_summary(context: dict) -> None:
    if not CONTRACTS_YAML.exists():
        context["contracts"] = {"error": "cross-layer-contracts.yaml 未找到"}
        return

    data = yaml.safe_load(CONTRACTS_YAML.read_text(encoding="utf-8"))
    contracts = data.get("contracts", [])

    p0_list: list[dict] = []
    p1_list: list[dict] = []

    for ctr in contracts:
        entry = {
            "id": ctr["id"],
            "name": ctr["name"],
            "flow": ctr.get("flow", ""),
            "frozen": ctr.get("frozen", False),
            "stability": ctr.get("stability", ""),
            "description_summary": ctr.get("description", "")[:120],
            "key_fields": [f["name"] for f in ctr.get("fields", []) if f.get("required", False)][:5],
            "has_sla": "sla" in ctr,
            "has_ai_prompt": "ai_prompt" in ctr,
        }
        if ctr.get("priority") == "P0":
            p0_list.append(entry)
        elif ctr.get("priority") == "P1":
            p1_list.append(entry)

    versioning = data.get("versioning_strategy", {})
    neg = versioning.get("cross_layer_version_negotiation", {})

    context["contracts"] = {
        "total": len(contracts),
        "p0": p0_list,
        "p1": p1_list,
        "version_negotiation_rules": [r["text"] for r in neg.get("rules", [])],
    }


def _extract_layer_summary(context: dict) -> None:
    layers: list[dict] = []
    for key, name in LAYER_NAMES.items():
        layers.append(
            {
                "id": key,
                "name": name,
                "order": int(key[1:]),
            }
        )
    context["layers"] = layers


def _extract_adr_summary(context: dict) -> None:
    adrs: list[dict] = []
    if not ADR_DIR.exists():
        context["adrs"] = []
        return

    for md_file in sorted(ADR_DIR.glob("adr-*.md")):
        content = md_file.read_text(encoding="utf-8", errors="replace")
        title = ""
        status = ""
        for line in content.split("\n")[:30]:
            stripped = line.strip()
            if stripped.startswith("# ") and not title:
                title = stripped[2:].strip()
            if stripped.startswith("status:") or stripped.startswith("Status:"):
                status = stripped.split(":", 1)[-1].strip()
        adrs.append(
            {
                "id": md_file.stem,
                "title": title[:100],
                "status": status,
            }
        )

    context["adrs"] = adrs


def _extract_governance_rules(context: dict) -> None:
    gov_dir = REPO_ROOT / "docs/01_policies_and_standards/governance"
    rules: list[dict] = []

    for domain_dir in sorted(gov_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for md_file in sorted(domain_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8", errors="replace")
            rule_count = sum(1 for line in content.split("\n") if line.strip().startswith("- "))
            rules.append(
                {
                    "domain": domain_dir.name,
                    "file": md_file.name,
                    "rules_approx": rule_count,
                }
            )

    context["governance"] = {
        "domains": len({r["domain"] for r in rules}),
        "documents": len(rules),
        "rule_files": rules,
    }


if __name__ == "__main__":
    main()
