# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_phase_rollback.py | §
# [MODULE] scripts.governance.vms_phase_rollback
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
VMS Phase 回滚方案 — MOD-INF-011 · TASK-INF-0217
===================================================
蓝图 §12 · P1 · 各 Phase 独立回滚能力

用法
----
    python scripts/governance/vms_phase_rollback.py --phase 1
    python scripts/governance/vms_phase_rollback.py --list
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PHASE_ROLLBACKS = {
    "1": {
        "name": "Phase 1: 基础设施对齐",
        "modules": [
            "provenance_enforcer.py",
            "embedding_router.py (降级模式可用)",
        ],
        "env_var": "VMS_PHASE1_MODE=degraded",
        "description": "禁用 provenance 强校验 + 嵌入模型降级为 InMemory 零向量",
    },
    "2": {
        "name": "Phase 2: 8 Collection 迁移",
        "modules": [
            "bridge_layer.py (关闭双读)",
            "vms_migrate.py (回滚迁移)",
        ],
        "env_var": "VMS_PHASE2_MODE=kb_only",
        "description": "恢复使用旧 kb/ 存储——所有 VMS 写入路由回 unified_memory_api",
    },
    "3": {
        "name": "Phase 3: 检索质量闭环",
        "modules": [
            "hybrid_retriever.py",
            "cross_collection_retriever.py",
            "retrieval_feedback.py",
        ],
        "env_var": "VMS_PHASE3_MODE=dense_only",
        "description": "禁用 BM25 + RRF，回退为纯向量检索",
    },
    "4": {
        "name": "Phase 4: 运维自动化",
        "modules": [
            "index_health_monitor.py (关闭自动修复)",
        ],
        "env_var": "VMS_PHASE4_MODE=monitor_only",
        "description": "仅监控不自动修复——schedule_maintenance 暂停",
    },
}

ROLLBACK_COMMANDS = {
    "1": [
        "set VMS_PHASE1_MODE=degraded",
        "set VMS_VALIDATE_PROVENANCE=False",
    ],
    "2": [
        "set VMS_PHASE2_MODE=kb_only",
        "set VMS_BRIDGE_DUAL_READ=False",
    ],
    "3": [
        "set VMS_PHASE3_MODE=dense_only",
        "set VMS_HYBRID_ENABLED=False",
    ],
    "4": [
        "set VMS_PHASE4_MODE=monitor_only",
        "set VMS_AUTO_REPAIR=False",
    ],
}


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="VMS Phase 回滚")
    parser.add_argument("--phase", choices=["1", "2", "3", "4"], help="回滚目标 Phase")
    parser.add_argument("--list", action="store_true", help="列出所有回滚方案")
    args = parser.parse_args()

    if args.list or not args.phase:
        print("VMS Phase 回滚方案")
        print("=" * 60)
        for phase_id, info in PHASE_ROLLBACKS.items():
            print(f"\nPhase {phase_id}: {info['name']}")
            print(f"  环境变量: {info['env_var']}")
            print(f"  描述:     {info['description']}")
            print(f"  模块:     {', '.join(info['modules'])}")
            print("  PowerShell 回滚命令:")
            for cmd in ROLLBACK_COMMANDS[phase_id]:
                print(f"    > {cmd}")
        return

    phase_id = args.phase
    info = PHASE_ROLLBACKS[phase_id]
    print(f"Phase {phase_id} 回滚: {info['name']}")
    print("=" * 60)
    print(f"环境变量: {info['env_var']}")
    print(f"描述: {info['description']}")
    print(f"受影响的模块: {', '.join(info['modules'])}")
    print(f"\n执行以下命令回滚 Phase {phase_id}:")
    for cmd in ROLLBACK_COMMANDS[phase_id]:
        print(f"  > {cmd}")


if __name__ == "__main__":
    main()
