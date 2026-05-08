"""
audit_trail.cli — MOD-INF-020 · CLI 审计面板
===============================================
蓝图 §8 · 命令行审计查询 + 完整性检查 + 统计面板 + 上下文 + 健康

用法
----
    python -m zephyr.audit_trail.cli search "keyword"
    python -m zephyr.audit_trail.cli verify
    python -m zephyr.audit_trail.cli stats
    python -m zephyr.audit_trail.cli trail [session_id]
    python -m zephyr.audit_trail.cli health
    python -m zephyr.audit_trail.cli query --agent <id>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def cmd_search(keyword: str) -> None:
    from zephyr.audit_trail.query import AuditQuery

    query = AuditQuery()
    results = query.search(keyword)
    print(f"Search results for '{keyword}': {len(results)} matches")
    for r in results[:20]:
        ts = r.get("timestamp", "?")[:19]
        agent = r.get("agent_id", "?")
        etype = r.get("event_type", "?")
        print(f"  {ts} | {agent} | {etype}")
    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more")


def cmd_verify() -> None:
    from zephyr.audit_trail.integrity import IntegrityVerifier

    verifier = IntegrityVerifier()
    result = verifier.verify_chain()
    if result["status"] == "valid":
        print(f"Chain integrity OK ({result['events_checked']} events)")
    elif result["status"] == "no_data":
        print("No audit data found")
    else:
        print(f"Chain COMPROMISED: {len(result['issues'])} issues")
        for issue in result["issues"]:
            print(f"  - {issue}")


def cmd_stats() -> None:
    from zephyr.audit_trail.self_monitor import SelfMonitor

    monitor = SelfMonitor()
    stats = monitor.check()
    print("Audit Trail Statistics")
    print("=" * 50)
    print(f"Total events:      {stats['total_events']}")
    print(f"File size:         {stats['file_size_mb']} MB")
    print(f"Throughput:        {stats['throughput_per_min']} events/min")
    print(f"Last event:        {stats['last_event_time'][:19]}")
    print(f"Health:            {'OK' if stats['healthy'] else 'WARNING: file too large'}")


def cmd_trail(session_id: str = "") -> None:
    from zephyr.audit_trail.query import AuditQuery

    query = AuditQuery()
    result = query.trail_for_ai_context(session_id)
    print(f"Audit Trail for AI Context")
    print(f"  Total events:    {result['total_events']}")
    print(f"  Recent events:   {result['recent_events']}")
    print(f"  Token estimate:  {result['token_estimate']}")
    print(f"  Within budget:   {result['within_budget']}")
    print()
    print(result["summary"])


def cmd_health() -> None:
    from zephyr.audit_trail.self_monitor import SelfMonitor
    from zephyr.audit_trail.integrity import IntegrityVerifier

    monitor = SelfMonitor()
    heartbeat = monitor.heartbeat()
    verifier = IntegrityVerifier()
    chain = verifier.verify_chain()

    all_ok = heartbeat["healthy"] and chain["status"] == "valid"
    status_icon = "PASS" if all_ok else "FAIL"

    print(f"Audit Health: [{status_icon}]")
    print(f"  Events:         {heartbeat['total_events']}")
    print(f"  File size:      {heartbeat['file_size_mb']} MB")
    print(f"  Chain status:   {chain['status']}")
    if chain.get("issues"):
        for issue in chain["issues"]:
            print(f"    - {issue}")


def cmd_query_agent(agent_id: str) -> None:
    from zephyr.audit_trail.query import AuditQuery

    query = AuditQuery()
    results = query.by_agent(agent_id)
    print(f"Agent '{agent_id}': {len(results)} events")
    for r in results[:20]:
        ts = r.get("timestamp", "?")[:19]
        etype = r.get("event_type", "?")
        target = r.get("target_path", r.get("operation", "?"))
        print(f"  {ts} | {etype} | {target}")


COMMANDS = {
    "search": lambda args: cmd_search(args[0] if args else ""),
    "verify": lambda _: cmd_verify(),
    "stats": lambda _: cmd_stats(),
    "trail": lambda args: cmd_trail(args[0] if args else ""),
    "health": lambda _: cmd_health(),
    "query": lambda args: cmd_query_agent(args[0] if args else ""),
}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m zephyr.audit_trail.cli <command> [args]")
        print("Commands: search | verify | stats | trail | health | query")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd in COMMANDS:
        COMMANDS[cmd](args)
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
