import os
import time

import yaml

REGISTRY = "data/asset_index/migration-registry.yaml"

RULINGS = {
    "src/zephyr/trading-contracts/": ("D_TRADING", "trading_contracts是交易域的合约定义，归D_TRADING"),
    "src/zephyr/health-monitor/": ("D_OPS", "健康监控是运维可观测性的一部分，归D_OPS"),
    "src/zephyr/context-engine/": ("D_AUTONOMY_CORE", "上下文引擎是AI自治核心的子模块，归D_AUTONOMY_CORE"),
    "src/zephyr/agent-spec/": ("D_AUTONOMY_CORE", "Agent规格定义是自治核心的一部分，归D_AUTONOMY_CORE"),
    "src/zephyr/semantic-auditor/": ("D_GOVERNANCE", "语义审计是治理域的一部分，归D_GOVERNANCE"),
    "src/zephyr/mcp/": ("D_INTEGRATION", "MCP工具集成属于集成域，归D_INTEGRATION"),
    "tests/": ("D_AUTONOMY_CORE", "tests/下无域子目录的测试文件，默认归自治核心（测试框架归属）"),
    "scripts/temp_audit/": ("D_GOVERNANCE", "临时审计报告归治理域"),
    "scripts/reports/": ("D_OPS", "运维报告归运维域"),
    "scripts/hooks/": ("D_GOVERNANCE", "Git hooks是治理流程的一部分，归D_GOVERNANCE"),
    "scripts/script_manifest.yaml": ("D_GOVERNANCE", "脚本清单是治理注册表的一部分，归D_GOVERNANCE"),
}


def apply_rulings():
    print("=== STEP 2C Ruling: Resolving 276 unassigned files ===")
    print()

    t0 = time.perf_counter()
    with open(REGISTRY, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  Loaded registry: {time.perf_counter() - t0:.2f}s")

    unassigned = data.get("unassigned_files", [])
    print(f"  Unassigned files: {len(unassigned)}")

    still_unassigned = []
    ruled_count = 0
    ruling_breakdown = {}

    for entry in unassigned:
        old_path = entry.get("old_state", {}).get("path", "")
        ruled = False

        for prefix, (domain, reason) in sorted(RULINGS.items(), key=lambda x: -len(x[0])):
            if old_path.startswith(prefix):
                entry["new_state"]["domain"] = domain
                entry["new_state"]["domain_group"] = ""
                entry["match_method"] = "ruling"
                entry["changes_required"] = [
                    {"type": "domain_assignment", "domain": domain},
                    {"type": "ruling_reason", "reason": reason},
                ]
                entry["status"] = "pending"
                ruled_count += 1
                ruling_breakdown[domain] = ruling_breakdown.get(domain, 0) + 1
                ruled = True
                break

        if not ruled:
            still_unassigned.append(entry)

    print(f"\n  Ruled: {ruled_count}")
    print(f"  Still unassigned: {len(still_unassigned)}")
    print("\n  Ruling breakdown:")
    for domain, count in sorted(ruling_breakdown.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")

    if still_unassigned:
        print("\n  Remaining unassigned files:")
        for entry in still_unassigned:
            path = entry.get("old_state", {}).get("path", "")
            ftype = entry.get("old_state", {}).get("type", "")
            print(f"    [{ftype}] {path}")

    data["unassigned_files"] = still_unassigned
    data["metadata"]["unassigned_count"] = len(still_unassigned)
    data["metadata"]["ruled_count"] = ruled_count

    entries = data.get("entries", [])
    for entry in unassigned:
        if entry.get("match_method") == "ruling":
            entries.append(entry)

    data["entries"] = entries
    data["metadata"]["total_entries"] = len(entries)

    coverage = (len(entries) - len(still_unassigned)) / len(entries) * 100 if entries else 0
    unassigned_rate = len(still_unassigned) / len(entries) * 100 if entries else 0
    data["metadata"]["coverage"] = round(coverage, 1)
    data["metadata"]["unassigned_rate"] = round(unassigned_rate, 2)

    tmp_path = REGISTRY + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, REGISTRY)
        print(f"\n  Written to {REGISTRY}")
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    print("\n=== RESULT ===")
    print(f"  Total entries: {len(entries)}")
    print(f"  Still unassigned: {len(still_unassigned)}")
    print(f"  Coverage: {coverage:.1f}%")
    print(f"  Unassigned rate: {unassigned_rate:.2f}%")


if __name__ == "__main__":
    apply_rulings()
