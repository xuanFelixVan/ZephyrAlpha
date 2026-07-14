# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_health_check.py | §
# [MODULE] scripts.governance.vms_health_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.__init__
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
VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动化
===========================================================
蓝图 §12.3 · 全面健康检查入口

用法
----
    python scripts/governance/vms_health_check.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS Health Check 脚本 — MOD-INF-011 · Phase 3 运维自动化
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from zephyr.governance.knowledge_management.vector_memory.collection_manager import CollectionManager
from zephyr.governance.knowledge_management.vector_memory.index_health_monitor import IndexHealthMonitor


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    print("VMS 健康检查")
    print("=" * 50)

    cm = CollectionManager()
    monitor = IndexHealthMonitor(cm)

    report = monitor.inspect_all()
    print(f"状态:   {report.status}")
    print(f"健康:   {report.collections_healthy}")
    print(f"不健康: {report.collections_unhealthy}")
    print(f"漂移:   {report.drift_detected}")
    print(f"检查时间: {report.checked_at}")
    print()

    if report.issues:
        print("问题:")
        for issue in report.issues:
            print(f"  ⚠️ {issue}")
        print()

    drift = monitor.detect_drift()
    if drift.drift_detected:
        print("漂移详情:")
        if drift.extra_collections:
            print(f"  多余 Collection: {drift.extra_collections}")
        if drift.missing_collections:
            print(f"  缺失 Collection: {drift.missing_collections}")
        print()

    ttl_reports = monitor.collect_ttl_expiry()
    expired_any = False
    for ttl in ttl_reports:
        if ttl.expired_count > 0:
            expired_any = True
            print(f"TTL 过期: {ttl.collection} ({ttl.expired_count}/{ttl.total_count})")

    if not expired_any:
        print("TTL: 无过期记录")

    integrity = monitor.integrity_check()
    print(f"\n完整性: {integrity['status']}")
    for issue in integrity.get("issues", []):
        print(f"  - {issue}")

    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "report": report.model_dump(),
        "ttl": [t.model_dump() for t in ttl_reports],
        "integrity": integrity,
        "drift": drift.model_dump(),
    }

    output_path = PROJECT_ROOT / "data/vector_db/_health_check_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n输出: {output_path}")


if __name__ == "__main__":
    main()
