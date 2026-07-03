"""查找true dual-header文件: 同时含A_config头和治理锚定块"""
import os
from pathlib import Path

root = Path(r"d:\ZephyrAlpha\docs\01_policies_and_standards")
dual_header = []
a_config_only = []
governance_only = []

for p in root.rglob("*.yaml"):
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        continue
    has_a_config = any(line.startswith("# [A_config]") for line in text.splitlines())
    has_governance = "# --- 治理锚定 ---" in text
    if has_a_config and has_governance:
        dual_header.append(str(p))
    elif has_a_config:
        a_config_only.append(str(p))
    elif has_governance:
        governance_only.append(str(p))

print(f"=== Dual-header (A_config + 治理锚定): {len(dual_header)} ===")
for f in dual_header:
    print(f"  {f}")
print(f"\n=== A_config only: {len(a_config_only)} ===")
print(f"=== Governance only: {len(governance_only)} ===")
