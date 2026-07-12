# [BLUEPRINT] MOD-INF-005 | scripts/governance/rebuild_audit_index.py | §
# [MODULE] scripts.governance.rebuild_audit_index
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_audit.indexer
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
scripts/governance/rebuild_audit_index.py — 重建 audit-trail SQLite 派生索引
==============================================================================
对标: MOD-DATABASE 数据库 + MOD-INF-020 audit-trail

用法:
    python scripts/governance/rebuild_audit_index.py              # 重建索引
    python scripts/governance/rebuild_audit_index.py --stats      # 仅显示统计
    python scripts/governance/rebuild_audit_index.py --warn-only  # 重建+警告模式
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import sys
from pathlib import Path

from _shared.constants import EXIT_PASS

_PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Rebuild audit-trail SQLite index")
    parser.add_argument("--stats", action="store_true", help="Only show stats, don't rebuild")
    parser.add_argument("--warn-only", action="store_true", help="Warn on errors, don't fail")
    args = parser.parse_args()

    try:
        from zephyr.gov_audit.indexer import AuditIndexer

        indexer = AuditIndexer()

        if args.stats:
            stats = indexer.query_stats()
            print(f"Total indexed events: {stats['total']}")
            print("\nBy event type:")
            for etype, cnt in stats.get("by_event_type", {}).items():
                print(f"  {etype}: {cnt}")
            print("\nBy agent:")
            for agent, cnt in stats.get("by_agent", {}).items():
                print(f"  {agent}: {cnt}")
            return EXIT_PASS

        result = indexer.rebuild()
        print(f"Index rebuild: {result.status}")
        print(f"  Events scanned:  {result.events_scanned}")
        print(f"  Events indexed:  {result.events_indexed}")
        print(f"  New entries:     {result.new_entries}")

        if result.errors:
            for err in result.errors:
                print(f"  ERROR: {err}")

        if result.status == "error":
            return 0 if args.warn_only else 1

        print("\nStats after rebuild:")
        stats = indexer.query_stats()
        print(f"  Total indexed: {stats['total']}")

        return EXIT_PASS

    except ImportError as e:
        print(f"Import error: {e}")
        return 0 if args.warn_only else 1
    except Exception as e:
        print(f"Error: {e}")
        return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
