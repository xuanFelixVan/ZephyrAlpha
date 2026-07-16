# [BLUEPRINT] MOD-INF-005 | scripts/context/generate_architecture_context.py | §
# [MODULE] scripts.context.generate_architecture_context
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
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
"""
generate_architecture_context.py — 预编译架构上下文包生成器

从 SSoT YAML + ADR + 治理文档中提取关键架构信息，压缩为 AI 可直接消费的
JSON 上下文包。解决 "每个 AI session 重新学习架构" 的问题。

输出: src/zephyr/context-engine/architecture-context.json

用法: python scripts/context/generate_architecture_context.py
      python scripts/context/generate_architecture_context.py --watch  # 文件变更自动重生成

SSoT: cross_layer_contracts.yaml + invariants.yaml + architecture_model/layers/*.yaml
       + ADR + governance + session/handoff + capacity_slo + gate/module registry + capability-heatmap
       + arch_guard manifest
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = SCRIPTS_DIR.parents[1]  # scripts/context/ -> repo root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import yaml
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

CONTRACTS_YAML = REPO_ROOT / (
    "architecture_model/contracts/cross_layer_contracts.yaml"
)
INVARIANTS_YAML = REPO_ROOT / (
    "architecture_model/cross_cutting/invariants.yaml"
)
LAYERS_DIR = REPO_ROOT / ("architecture_model/layers")
ADR_DIR = REPO_ROOT / "docs/02_enterprise_architecture/adr"
OUTPUT_PATH = REPO_ROOT / "src/zephyr/context-engine/architecture-context.json"
handoff_DIR = REPO_ROOT / "docs/19_development_workspace/handoff-logs"
CAPACITY_SLO_YAML = REPO_ROOT / "config" / "capacity_slo.yaml"
GATE_REGISTRY_YAML = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"
MODULE_REGISTRY_YAML = REPO_ROOT / "docs/03_modules/module-registry.yaml"
CAPABILITY_HEATMAP_YAML = (
    REPO_ROOT
    / "architecture_model/cross_cutting/capability_heatmap.yaml"
)
ARCH_GUARD_MANIFEST = REPO_ROOT / "scripts/arch_guard/manifest.yaml"

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
        "version": "3.1",
        "schema": "zephyr-alpha-architecture-context/v1",
    }

    _extract_contracts_summary(context)
    _extract_invariants(context)
    _extract_layer_summary(context)
    _extract_adr_summary(context)
    _extract_governance_rules(context)
    _extract_session_logs(context)
    _extract_handoff_logs(context)
    _extract_capacity_slo(context)
    _extract_gate_registry(context)
    _extract_module_registry(context)
    _extract_capability_heatmap(context)
    _extract_arch_guard_manifest(context)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{OUTPUT_PATH}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(
            json.dumps(context, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp_path, OUTPUT_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    print(f"[ArchContext] 预编译架构上下文已生成 → {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  - P0 契约: {len(context.get('contracts', {}).get('p0', []))} 条")
    print(f"  - P1 契约: {len(context.get('contracts', {}).get('p1', []))} 条")
    print(f"  - 不变量: {context.get('invariants', {}).get('total', 0)} 条")
    print(f"  - 层定义: {len(context.get('layers', []))} 层")
    print(f"  - ADR: {len(context.get('adrs', []))} 份")
    sessions_count = len(context.get("sessions", {}).get("recent", []))
    if sessions_count:
        print(f"  - 最近 Session: {sessions_count} 条")
    ho = context.get("handoffs", {})
    if ho.get("total", 0):
        print(f"  - Handoff 日志: {ho.get('total', 0)} 份（列出最近 {len(ho.get('recent', []))} 条）")
    slo = context.get("capacity_slo") or {}
    if slo.get("sli_count", 0):
        print(f"  - SLI 注册: {slo.get('sli_count')} 条（MOD-INF-001）")
    gates = (context.get("gate_registry") or {}).get("total_gates")
    if gates is not None:
        print(f"  - 治理 GATE 登记: {gates}")
    modc = (context.get("module_registry") or {}).get("module_count")
    if modc is not None:
        print(f"  - 模块登记: {modc}")


def _extract_contracts_summary(context: dict) -> None:
    if not CONTRACTS_YAML.exists():
        context["contracts"] = {"error": "cross_layer_contracts.yaml 未找到"}
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


def _extract_invariants(context: dict) -> None:
    if not INVARIANTS_YAML.exists():
        context["invariants"] = {"error": "invariants.yaml 未找到", "total": 0, "items": []}
        return
    data = yaml.safe_load(INVARIANTS_YAML.read_text(encoding="utf-8"))
    invs: list[dict] = data.get("invariants") or []
    context["invariants"] = {
        "total": len(invs),
        "items": [
            {
                "id": row.get("id"),
                "category": row.get("category"),
                "statement": row.get("statement"),
                "priority": row.get("priority"),
                "enforcement": row.get("enforcement"),
                "fitness_function_path": row.get("fitness_function_path"),
                "owner": row.get("owner"),
            }
            for row in invs
        ],
    }


def _extract_layer_summary(context: dict) -> None:
    layers: list[dict] = []
    if LAYERS_DIR.exists():
        for yf in sorted(LAYERS_DIR.glob("l*.yaml")):
            try:
                data = yaml.safe_load(yf.read_text(encoding="utf-8", errors="replace")) or {}
            except Exception:
                continue
            part = data.get("partition") or {}
            mods = data.get("modules") or []
            lid = str(part.get("id") or yf.stem.split("-")[0] or "")
            cn = LAYER_NAMES.get(lid, "")
            layers.append(
                {
                    "id": lid,
                    "name": part.get("name") or cn or lid,
                    "name_zh": cn or None,
                    "layer_position": part.get("layer_position"),
                    "runtime_plane": part.get("runtime_plane"),
                    "module_count": len(mods),
                    "source_file": str(yf.relative_to(REPO_ROOT)).replace("\\", "/"),
                }
            )
    if not layers:
        for key, name in LAYER_NAMES.items():
            layers.append({"id": key, "name": name, "layer_position": int(key[1:])})
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


def _extract_session_logs(context: dict) -> None:
    session_dir = REPO_ROOT / "session_logs"
    if not session_dir.exists():
        context["sessions"] = {"recent": [], "total": 0}
        return

    index_file = session_dir / "index.yaml"
    total = 0
    stats = {}

    if index_file.exists():
        try:
            index_data = yaml.safe_load(index_file.read_text(encoding="utf-8"))
            total = index_data.get("total_sessions", 0)
            stats = index_data.get("stats", {})
        except Exception:
            pass

    recent: list[dict] = []
    yaml_files = sorted(session_dir.rglob("session-*.yaml"))
    yaml_files = yaml_files[:10]

    for yf in yaml_files:
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8", errors="replace"))
            recent.append(
                {
                    "id": data.get("session_id", yf.stem),
                    "date": data.get("date", ""),
                    "phase": data.get("current_phase", ""),
                    "agent": data.get("author_agent", ""),
                }
            )
        except Exception:
            pass

    context["sessions"] = {
        "recent": recent,
        "total": total,
        "stats": stats,
        "index_version": stats.get("index_version", "1.0"),
    }


def _extract_handoff_logs(context: dict) -> None:
    if not handoff_DIR.is_dir():
        context["handoffs"] = {"recent": [], "total": 0}
        return
    all_md = sorted(handoff_DIR.glob("handoff-*.md"))
    tail = all_md[-10:] if len(all_md) > 10 else all_md
    recent = [{"file": str(p.relative_to(REPO_ROOT)).replace("\\", "/")} for p in tail]
    context["handoffs"] = {
        "recent": recent,
        "total": len(all_md),
    }


def _extract_capacity_slo(context: dict) -> None:
    if not CAPACITY_SLO_YAML.is_file():
        context["capacity_slo"] = {"error": "未找到 capacity_slo.yaml"}
        return
    data = yaml.safe_load(CAPACITY_SLO_YAML.read_text(encoding="utf-8")) or {}
    reg = data.get("slo_registry") or []
    context["capacity_slo"] = {
        "path": str(CAPACITY_SLO_YAML.relative_to(REPO_ROOT)).replace("\\", "/"),
        "schema_version": data.get("schema_version"),
        "module_ref": data.get("module_ref"),
        "sli_count": len(reg) if isinstance(reg, list) else 0,
        "sli_ids": [r.get("id") for r in reg if isinstance(r, dict) and r.get("id")],
        "arch_guard_keys": list((data.get("arch_guard") or {}).keys()),
    }


def _extract_gate_registry(context: dict) -> None:
    if not GATE_REGISTRY_YAML.is_file():
        context["gate_registry"] = {"error": "未找到 gate_registry.yaml"}
        return
    data = yaml.safe_load(GATE_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
    gates = data.get("gates") or []
    context["gate_registry"] = {
        "path": str(GATE_REGISTRY_YAML.relative_to(REPO_ROOT)).replace("\\", "/"),
        "total_gates": data.get("total_gates", len(gates) if isinstance(gates, list) else 0),
        "source": data.get("source"),
        "gates_preview": [
            {"gate_id": g.get("gate_id"), "name": (g.get("name") or "")[:80], "status": g.get("status")}
            for g in gates[:20]
            if isinstance(g, dict)
        ],
    }


def _extract_module_registry(context: dict) -> None:
    if not MODULE_REGISTRY_YAML.is_file():
        context["module_registry"] = {"error": "未找到 module-registry.yaml"}
        return
    data = yaml.safe_load(MODULE_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
    modules = data.get("modules") or []
    context["module_registry"] = {
        "path": str(MODULE_REGISTRY_YAML.relative_to(REPO_ROOT)).replace("\\", "/"),
        "module_count": len(modules) if isinstance(modules, list) else 0,
        "schema_layers": len((data.get("_schema") or {}).get("layers") or []) if data.get("_schema") else None,
    }


def _extract_capability_heatmap(context: dict) -> None:
    if not CAPABILITY_HEATMAP_YAML.is_file():
        context["capability_heatmap"] = {"error": "未找到 capability_heatmap.yaml"}
        return
    data = yaml.safe_load(CAPABILITY_HEATMAP_YAML.read_text(encoding="utf-8")) or {}
    part = data.get("partition") or {}
    caps = data.get("capabilities") or []
    n = len(caps) if isinstance(caps, list) else 0
    context["capability_heatmap"] = {
        "path": str(CAPABILITY_HEATMAP_YAML.relative_to(REPO_ROOT)).replace("\\", "/"),
        "partition_id": part.get("id"),
        "partition_name": part.get("name"),
        "overall_maturity_level": part.get("overall_maturity_level"),
        "overall_maturity_score": part.get("overall_maturity_score"),
        "capability_entries": n,
    }


def _extract_arch_guard_manifest(context: dict) -> None:
    if not ARCH_GUARD_MANIFEST.is_file():
        context["arch_guard"] = {"error": "未找到 manifest.yaml"}
        return
    data = yaml.safe_load(ARCH_GUARD_MANIFEST.read_text(encoding="utf-8")) or {}
    ffs = data.get("fitness_functions") or []
    context["arch_guard"] = {
        "manifest_path": str(ARCH_GUARD_MANIFEST.relative_to(REPO_ROOT)).replace("\\", "/"),
        "fitness_count": len(ffs) if isinstance(ffs, list) else 0,
        "fitness_active": sum(1 for f in ffs if isinstance(f, dict) and f.get("status") == "active"),
        "fitness_ids": [f.get("id") for f in ffs if isinstance(f, dict) and f.get("id")],
    }


if __name__ == "__main__":
    main()
