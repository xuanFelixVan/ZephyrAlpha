# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_idempotency_key.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_idempotency_key
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
check_idempotency_key.py — 幂等 Key 字段存在性检查 (INV-007)

INV-007: 所有跨层事件必须携带幂等 Key（Idempotency Key）：防止重复处理。

检测方式：
  - 读取 cross_layer_contracts.yaml
  - 检查所有 P0 DATA / ERROR / BACKPRESSURE 契约的 fields 中是否包含 idempotency_key
  - 对于已 codegen 的契约，检查对应的 Python dataclass 是否包含该字段

注意：本脚本检查的是"字段是否存在"，不是"运行时是否使用"。
      运行时校验由 ContractEnforcer 完成。

exit: 0=pass, 1=missing field found
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

CONTRACTS_YAML = (
    REPO_ROOT
    / "architecture_model"
    / "contracts"
    / "cross_layer_contracts.yaml"
)

CONTRACT_TYPES_TO_CHECK = ["P0", "P1"]

def main() -> int:
    if not CONTRACTS_YAML.exists():
        print(f"契约文件不存在: {CONTRACTS_YAML}")
        return 2

    with open(CONTRACTS_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    contracts: list[dict] = data.get("contracts", [])
    missing: list[str] = []

    for ctr in contracts:
        ctr_id = ctr.get("id", "UNKNOWN")
        priority = ctr.get("priority", "")
        name = ctr.get("name", "")

        if priority not in CONTRACT_TYPES_TO_CHECK:
            continue

        fields: list[dict] = ctr.get("fields", [])
        field_names = [f.get("name", "") for f in fields]

        if "idempotency_key" not in field_names:
            missing.append(f"  {ctr_id} ({priority}) {name}")

    if missing:
        print(f"❌ INV-007 幂等 Key —— {len(missing)} 条契约缺少 idempotency_key 字段:")
        for m in missing:
            print(m)
        print()
        print("INV-007 要求：所有跨层事件 MUST 携带 idempotency_key 字段。")
        print("修复方式：在各契约 YAML 的 fields 中添加：")
        print('  - {name: idempotency_key, type: str, required: true, description: "幂等键（UUID）"}')
        return 1

    print("✅ INV-007 幂等 Key —— 所有 P0/P1 契约均包含 idempotency_key 字段")
    return 0

if __name__ == "__main__":
    sys.exit(main())
