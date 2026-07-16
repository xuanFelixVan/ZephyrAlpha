# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_capacity_slo_ssot.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_capacity_slo_ssot
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
check_capacity_slo_ssot.py — capacity_slo.yaml 注册表 + 与 invariants 数字对齐（SSoT 闭环）

校验：
  - config/capacity_slo.yaml 存在且 slo_registry >= min_slo_entries（默认 8）
  - arch_guard.invariant_numeric_alignment 与 invariants.yaml 中 INV-001 / INV-015 的 ms 声明一致

exit: 0=pass, 1=fail, 2=config missing
"""

from __future__ import annotations

import sys
from pathlib import Path

# 包内导入：以脚本方式运行时补全 path
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from _arch_ssot import (  # noqa: E402
    CAPACITY_SLO_PATH,
    INVARIANTS_PATH,
    get_inv_numeric_targets_by_id,
    load_yaml,
)


def main() -> int:
    if not CAPACITY_SLO_PATH.is_file():
        print(f"FAIL: 缺少 {CAPACITY_SLO_PATH.relative_to(CAPACITY_SLO_PATH.parents[2])}")
        return 2

    slo = load_yaml(CAPACITY_SLO_PATH)
    inv = load_yaml(INVARIANTS_PATH)
    registry = slo.get("slo_registry") or []
    if not isinstance(registry, list):
        print("FAIL: slo_registry 必须为列表")
        return 1

    ag = slo.get("arch_guard") or {}
    min_entries = int(ag.get("min_slo_entries", 8))
    if len(registry) < min_entries:
        print(f"FAIL: slo_registry 条目数 {len(registry)} < 要求 {min_entries}")
        return 1

    ids = {row.get("id") for row in registry if isinstance(row, dict)}
    need_cap009 = ag.get("invariant_numeric_alignment", {}).get("INV-001", {}).get("slo_id")
    if need_cap009 and need_cap009 not in ids:
        print(f"FAIL: 缺少 SLO {need_cap009}")
        return 1

    align = ag.get("invariant_numeric_alignment") or {}
    inv_nums = get_inv_numeric_targets_by_id(inv)

    for iid, cfg in align.items():
        if iid not in inv_nums:
            continue
        expected_ms = inv_nums[iid]
        got = cfg.get("max_latency_ms")
        if got is None:
            print(f"FAIL: {iid} 在 capacity_slo 中缺少 max_latency_ms")
            return 1
        if int(got) != int(expected_ms):
            print(f"FAIL: {iid} 毫秒不一致 invariants={expected_ms} capacity_slo.arch_guard={got}")
            return 1

    print(f"OK: capacity_slo 注册 {len(registry)} 条 SLI，与 invariants 数字对齐")
    return 0


if __name__ == "__main__":
    sys.exit(main())
