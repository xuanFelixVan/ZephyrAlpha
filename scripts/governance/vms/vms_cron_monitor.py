# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_cron_monitor.py | §
# [MODULE] scripts.governance.vms_cron_monitor
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
VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224
===============================================
P2 · 运维基础设施收尾——定时 task 封装

模式
----
- cron: 一次性执行所有检查后退出（适合 Windows Task Scheduler）
- daemon: 持续运行，按 interval_seconds 循环检查（适合长期监控）

用法
----
    python scripts/governance/vms_cron_monitor.py          # cron 模式
    python scripts/governance/vms_cron_monitor.py --daemon  # daemon 模式
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS Cron 监控器 — MOD-INF-011 · TASK-INF-0224
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_logger = logging.getLogger("vms_cron")


def run_cycle() -> dict[str, Any]:
    """run_cycle implementation."""
    from zephyr.governance.knowledge_management.vector_memory.collection_manager import CollectionManager
    from zephyr.governance.knowledge_management.vector_memory.index_health_monitor import IndexHealthMonitor

    now = datetime.now(UTC).isoformat()
    cm = CollectionManager()
    monitor = IndexHealthMonitor(cm)

    report = monitor.inspect_all()
    drift = monitor.detect_drift()
    ttl = monitor.collect_ttl_expiry()
    integrity = monitor.integrity_check()

    total_issues = len(report.issues)
    is_healthy = report.status == "healthy"

    result = {
        "timestamp": now,
        "healthy": is_healthy,
        "collection_count": report.collections_healthy + report.collections_unhealthy,
        "healthy_count": report.collections_healthy,
        "issue_count": total_issues,
        "drift_detected": drift.drift_detected,
        "ttl_expired_total": sum(t.expired_count for t in ttl),
        "integrity": integrity["status"],
    }

    output_dir = PROJECT_ROOT / "data" / "vector_db"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "cron_monitor_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    if not is_healthy:
        _logger.warning("VMS 不健康: %d 个问题", total_issues)
        for issue in report.issues:
            _logger.warning("  - %s", issue)
    else:
        _logger.info(
            "VMS 健康: %d/%d collections OK",
            report.collections_healthy,
            report.collections_healthy + report.collections_unhealthy,
        )

    return result


def run_cron() -> None:
    """run_cron implementation."""
    _logger.info("VMS Cron Monitor: 执行一次性检查")
    result = run_cycle()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    _logger.info("VMS Cron Monitor: 检查完成")


def run_daemon(interval_seconds: int = 3600) -> None:
    """run_daemon implementation."""
    _logger.info("VMS Cron Monitor: 启动 daemon 模式 (间隔=%ds)", interval_seconds)
    try:
        while True:
            run_cycle()
            _logger.info("等待 %d 秒后执行下一次检查...", interval_seconds)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        _logger.info("VMS Cron Monitor: daemon 已停止")


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="VMS Cron Monitor")
    parser.add_argument("--daemon", action="store_true", help="持续运行模式")
    parser.add_argument("--interval", type=int, default=3600, help="Daemon 检查间隔 (秒)")
    args = parser.parse_args()

    if args.daemon:
        run_daemon(args.interval)
    else:
        run_cron()


if __name__ == "__main__":
    main()
