# [BLUEPRINT] MOD-INF-005 | scripts/governance/ri_build_completion_check.py | §
# [MODULE] scripts.governance.ri_build_completion_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
# [TTL] task_bound
"""
Runtime Integration Phase 2 完工验证 — MOD-INF-002
=====================================================
蓝图 §7 · v5.0.1 · 验证 15 RI 模块 + Cross-Layer 依赖完整性

用法
----
    python scripts/governance/ri_build_completion_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RI_MODULES = [
    ("RI-01", "Event Bus", "zephyr.shared.event_bus"),
    ("RI-02", "Memory Trio", "zephyr.integration.vector_memory"),
    ("RI-03", "Structured Concurrency", "zephyr.shared.concurrency"),
    ("RI-04", "Bulkhead", "zephyr.shared.bulkhead"),
    ("RI-05", "Graceful Shutdown", "zephyr.shared.shutdown"),
    ("RI-06", "Load Shedding", "zephyr.shared.load_shedding"),
    ("RI-07", "W3C Trace Context", "zephyr.shared.tracing"),
    ("RI-08", "Session Undo", "zephyr.shared.session_undo"),
    ("RI-09", "Owner Mental Budget", "zephyr.shared.mental_budget"),
    ("RI-10", "Leader Election", "zephyr.shared.leader_election"),
    ("RI-11", "Module Sandbox", "zephyr.shared.sandbox"),
    ("RI-12", "Sleep Time Protocol", "zephyr.shared.sleep_protocol"),
    ("RI-13", "Auto Deciding Engine", "zephyr.shared.auto_decide"),
    ("RI-14", "Prompt Cache", "zephyr.shared.prompt_cache"),
    ("RI-15", "Model Fallback", "zephyr.shared.model_fallback"),
]

CROSS_LAYER_CHECKS = [
    ("VMS ↔ CE", "src/zephyr/vector-memory/vector_bridge.py"),
    ("VMS ↔ KB", "src/zephyr/vector-memory/bridge_layer.py"),
    ("Audit ↔ Writer", "src/zephyr/audit-trail/writer.py"),
    ("Audit ↔ Signer", "src/zephyr/audit-trail/agent_signer.py"),
    ("Audit ↔ Integrity", "src/zephyr/audit-trail/integrity.py"),
]


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    print("Runtime Integration Build 完成检查")
    print("=" * 55)

    passed = 0
    total = 0

    print("\n15 RI 模块检查:")
    for ri_id, name, module_path in RI_MODULES:
        total += 1
        try:
            mod = __import__(module_path, fromlist=["_"])
            passed += 1
            print(f"  ✅ {ri_id} {name:<25s} → {module_path}")
        except ImportError:
            print(f"  ⚠️ {ri_id} {name:<25s} → {module_path} (尚未实现)")

    print("\nCross-Layer 文件检查:")
    for name, path in CROSS_LAYER_CHECKS:
        total += 1
        file_path = PROJECT_ROOT / path
        if file_path.exists():
            passed += 1
            print(f"  ✅ {name:<20s} → {path}")
        else:
            print(f"  ❌ {name:<20s} → {path} (缺失)")

    print(f"\n结果: {passed}/{total} 通过")

    if passed == total:
        print("✅ Runtime Integration 全部通过!")
    else:
        print(f"⚠️ {total - passed} 项未通过")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
