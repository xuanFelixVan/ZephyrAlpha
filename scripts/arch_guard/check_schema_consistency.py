# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_schema_consistency.py | §
# [MODULE] scripts.arch_guard.check_schema_consistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
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
check_schema_consistency.py — INV-010 契约物理路径存在性（Schema canonical 基线）

  - shared/contracts 中在 YAML 登记的 physical_path 对应的 Python 文件必须存在

exit: 0=pass, 1=fail
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CONTRACTS_PATH, load_yaml  # noqa: E402

def main() -> int:
    data = load_yaml(CONTRACTS_PATH)
    contracts = data.get("contracts") or []
    missing: list[str] = []
    for c in contracts:
        if not isinstance(c, dict):
            continue
        rel = c.get("physical_path") or ""
        if not isinstance(rel, str) or not rel.startswith("src/zephyr/shared/contracts/"):
            continue
        if not (REPO_ROOT / rel).is_file():
            missing.append(f"{c.get('id')} -> {rel}")

    if missing:
        print("FAIL: 以下契约 physical_path 缺失（INV-010）:")
        for m in missing:
            print(f"  - {m}")
        return 1

    print(f"OK: {len(contracts)} 条契约条目扫描，shared/contracts physical_path 均存在")
    return 0

if __name__ == "__main__":
    sys.exit(main())
