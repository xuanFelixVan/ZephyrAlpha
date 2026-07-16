# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_build_completion_check.py | §
# [MODULE] scripts.governance.vms_build_completion_check
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
# [TTL] permanent
"""
VMS Build Completion Check — MOD-INF-011 · TASK-INF-0217
==========================================================
Phase 1 完成自检: 验证 6 模块全部可用 + 无 import error

用法
----
    python scripts/governance/vms_build_completion_check.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS Build Completion Check — MOD-INF-011 · TASK-INF-0217
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    checks: list[tuple[str, bool, str]] = []

    modules = [
        ("collection_manager", "zephyr.integration.vector_memory.collection_manager", "CollectionManager"),
        ("embedding_router", "zephyr.integration.vector_memory.embedding_router", "EmbeddingRouter"),
        ("chunk_strategy_router", "zephyr.integration.vector_memory.chunk_strategy_router", "ChunkStrategyRouter"),
        ("hybrid_retriever", "zephyr.integration.vector_memory.hybrid_retriever", "HybridRetriever"),
        ("provenance_enforcer", "zephyr.integration.vector_memory.provenance_enforcer", "ProvenanceEnforcer"),
        ("index_health_monitor", "zephyr.integration.vector_memory.index_health_monitor", "IndexHealthMonitor"),
        ("retrieval_feedback", "zephyr.integration.vector_memory.retrieval_feedback", "RetrievalFeedback"),
        ("cache_layer", "zephyr.integration.vector_memory.cache_layer", "CacheLayer"),
        ("bridge_layer", "zephyr.integration.vector_memory.bridge_layer", "BridgeLayer"),
        ("vector_bridge", "zephyr.integration.vector_memory.vector_bridge", "VectorBridge"),
        (
            "cross_collection_retriever",
            "zephyr.integration.vector_memory.cross_collection_retriever",
            "CrossCollectionRetriever",
        ),
        ("in_memory_backend", "zephyr.integration.vector_memory.in_memory_memory_backend", "InMemoryMemoryBackend"),
        ("vms_schemas", "zephyr.integration.vector_memory.vms_schemas", "ScoredHit"),
    ]

    print("VMS Build 完成检查")
    print("=" * 50)

    for name, module_path, class_name in modules:
        try:
            mod = __import__(module_path, fromlist=[class_name])
            getattr(mod, class_name)
            checks.append((name, True, "OK"))
        except Exception as e:
            checks.append((name, False, str(e)[:60]))

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)

    for name, ok, msg in checks:
        status = "✅" if ok else "❌"
        print(f"  {status} {name:<30s} {msg}")

    print(f"\n结果: {passed}/{total} 通过")
    if passed == total:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
