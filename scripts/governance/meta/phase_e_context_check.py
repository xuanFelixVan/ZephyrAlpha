# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/phase_e_context_check.py | §
# [MODULE] scripts.governance.meta.phase_e_context_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""Phase E: AI context injection verification script"""

import glob

import yaml

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


layers = ["l00", "l01", "l02", "l03", "l04", "l05", "l06", "l07", "l08", "l09", "l10", "l11", "l12", "l13"]
print("=== Layer __init__.py CTR declarations ===")
all_ok = True
for l in layers:
    path = f"src/zephyr/{l}_*/__init__.py"
    matches = glob.glob(path)
    if matches:
        # 5.169 修复：用 context manager 防止文件句柄泄漏
        with open(matches[0], encoding="utf-8") as _f:
            content = _f.read()
        has_producer = "Producer" in content
        has_consumer = "Consumer" in content
        has_ctr = "CTR-" in content
        status = "OK" if (has_ctr and (has_producer or has_consumer)) else "MISSING"
        if status != "OK":
            all_ok = False
        print(f"  {l}: Producer={has_producer}, Consumer={has_consumer}, CTR_refs={has_ctr} -> {status}")
    else:
        print(f"  {l}: NOT FOUND")
        all_ok = False

print()
print("=== Baseline files ===")
for f in sorted(glob.glob("scripts/governance/meta/baselines/*.jsonl")):
    # 5.169 修复：用 context manager 防止文件句柄泄漏
    with open(f, encoding="utf-8") as _f:
        lines = _f.readlines()
    print(f"  {f}: {len(lines)} findings")

print()
print("=== Shadow mode ===")
with open("scripts/governance/meta/shadow_mode_state.yaml", encoding="utf-8") as f:
    d = yaml.safe_load(f)
scripts = d.get("scripts", {})
print(f"  Registered scripts: {len(scripts)}")
for name, info in scripts.items():
    print(f"    - {name}: stage={info.get('stage', '?')}")

print()
print("=== CTR contracts ===")
with open(
    "architecture_model/contracts/cross_layer_contracts.yaml",
    encoding="utf-8",
) as f:
    contracts = yaml.safe_load(f)
ctr_list = contracts.get("contracts", [])
ctr_count = sum(1 for c in ctr_list if "ctr_id" in c)
p0_count = sum(1 for c in ctr_list if c.get("priority") == "P0")
p1_count = sum(1 for c in ctr_list if c.get("priority") == "P1")
print(f"  Total: {ctr_count} (P0={p0_count}, P1={p1_count})")

print()
print("=== Architecture model layers ===")
layer_files = glob.glob("architecture_model/layers/*.yaml")
print(f"  Layer YAML files: {len(layer_files)}")

print()
print("=== Gate registry ===")
with open("src/zephyr/gates/_registry.yaml", encoding="utf-8") as f:
    reg = yaml.safe_load(f)
active = sum(1 for g in reg.get("gates", []) if g.get("status") == "active")
impl = sum(1 for g in reg.get("gates", []) if g.get("status") == "implemented")
print(f"  Gates: {len(reg.get('gates', []))} (active={active}, implemented={impl})")

print()
print(f"=== OVERALL: {'ALL PASS' if all_ok else 'SOME ISSUES'} ===")
