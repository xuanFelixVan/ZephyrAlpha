# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_kill_switch_latency.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_kill_switch_latency
# [DOMAIN] D_AUTONOMY_PERM
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
check_kill_switch_latency.py — Kill Switch 延迟门禁 (INV-001)

  - SSoT：config/capacity_slo.yaml → CAP-009 / arch_guard.invariant_numeric_alignment.INV-001
  - T0 实测：ZEPHYR_T1_KILL_SWITCH_PROBE=1 时运行 KillSwitchSimulator 健康检查
  - T1 硬件预留：register_ack_callback() 接口支持真实 GPIO 中断

exit: 0=pass, 1=fail, 2=config error
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

from _arch_ssot import CAPACITY_SLO_PATH, load_yaml  # noqa: E402

def main() -> int:
    if not CAPACITY_SLO_PATH.is_file():
        print("FAIL: 缺少 config/capacity_slo.yaml")
        return 2

    slo = load_yaml(CAPACITY_SLO_PATH)
    cap_ids = {row.get("id") for row in (slo.get("slo_registry") or []) if isinstance(row, dict)}
    if "CAP-009-kill-switch-trigger-latency" not in cap_ids:
        print("FAIL: slo_registry 缺少 CAP-009-kill-switch-trigger-latency")
        return 1

    cap9 = next(
        r
        for r in (slo.get("slo_registry") or [])
        if isinstance(r, dict) and r.get("id") == "CAP-009-kill-switch-trigger-latency"
    )
    target = cap9.get("target_ms")
    if target is None:
        print("FAIL: CAP-009 缺少 target_ms")
        return 1

    inv_align = (slo.get("arch_guard") or {}).get("invariant_numeric_alignment", {}).get("INV-001", {})
    max_ms = inv_align.get("max_latency_ms")
    if max_ms is not None and int(max_ms) != int(target):
        print(f"FAIL: CAP-009.target_ms={target} 与 arch_guard.INV-001.max_latency_ms={max_ms} 不一致")
        return 1

    if os.environ.get("ZEPHYR_T1_KILL_SWITCH_PROBE") == "1":
        sim_path = REPO_ROOT / "src" / "zephyr" / "infrastructure_runtime_integration" / "kill_switch_sim.py"
        if not sim_path.exists():
            print("WARN: ZEPHYR_T1_KILL_SWITCH_PROBE=1 但 kill_switch_sim.py 不存在")
            return 0

        import importlib.util

        spec = importlib.util.spec_from_file_location("kill_switch_sim", sim_path)
        if spec and spec.loader:
            sim_mod = importlib.util.module_from_spec(spec)
            sys.modules["kill_switch_sim"] = sim_mod
            spec.loader.exec_module(sim_mod)
            sim = sim_mod.KillSwitchSimulator(target_ms=target)
            ok = sim.health_check()
            if ok:
                print(f"OK: INV-001 Kill Switch T0 实测 — 延迟达标的 target_ms={target}ms")
                return 0
            else:
                print(f"FAIL: INV-001 Kill Switch T0 实测 — 延迟超标! target_ms={target}ms")
                return 1

    print(
        f"OK: INV-001 Kill Switch — CAP-009 target_ms={target}（声明级）；"
        " 设置 ZEPHYR_T1_KILL_SWITCH_PROBE=1 启用 T0 实测。"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
