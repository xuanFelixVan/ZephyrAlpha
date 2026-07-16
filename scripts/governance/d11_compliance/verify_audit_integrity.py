# [BLUEPRINT] MOD-INF-005 | scripts/governance/verify_audit_integrity.py | §
# [MODULE] scripts.governance.verify_audit_integrity
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
#!/usr/bin/env python3
"""
verify_audit_integrity.py — MOD-INF-020 · 零依赖外部独立验证器
=================================================================
蓝图 §5.6 · Phase scaffold 验收标准 #5

零依赖：纯标准库，不依赖 Pydantic / cryptography / zephyr 项目。
任何环境都可直接运行，只需 events.jsonl 文件。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: verify_audit_integrity.py — MOD-INF-020 · 零依赖外部独立验证器
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import hashlib
import json
import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS


def verify_jsonl_chain(jsonl_path: str) -> dict:
    """verify_jsonl_chain implementation."""
    issues = []
    prev_hash = ""
    event_count = 0

    try:
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event_count += 1
                event = json.loads(line)

                stored_prev = event.get("prev_entry_hash", event.get("prev_hash", ""))
                if stored_prev != prev_hash:
                    issues.append(
                        f"Line {event_count}: prev_entry_hash mismatch. "
                        f"Expected {prev_hash[:16] if prev_hash else 'empty'}..., "
                        f"Got {stored_prev[:16] if stored_prev else 'empty'}..."
                    )

                event_str = json.dumps(event, ensure_ascii=False, sort_keys=True, default=str)
                prev_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()

    except FileNotFoundError:
        return {"status": "no_data", "events_checked": 0, "issues": ["File not found"]}
    except PermissionError:
        return {"status": "error", "events_checked": 0, "issues": ["Permission denied"]}
    except json.JSONDecodeError as e:
        return {"status": "error", "events_checked": event_count, "issues": [f"JSON parse error: {e}"]}

    status = "valid" if not issues else "compromised"
    return {
        "status": status,
        "events_checked": event_count,
        "issues": issues,
        "final_chain_hash": prev_hash[:40] if prev_hash else "N/A",
    }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Zero-dependency audit trail integrity verifier")
    parser.add_argument(
        "jsonl",
        nargs="?",
        default="data/audit-trail/events.jsonl",
        help="Path to events.jsonl (default: data/audit-trail/events.jsonl)",
    )
    parser.add_argument("--warn-only", action="store_true", help="Always exit 0 (for safety in automated scans)")
    args = parser.parse_args()

    result = verify_jsonl_chain(args.jsonl)

    if result["status"] == "valid":
        print(f"VERIFIED: {result['events_checked']} events, chain intact")
    elif result["status"] == "no_data":
        print("NO_DATA: Audit log not found")
    elif result["status"] == "error":
        print(f"ERROR: {result['issues'][0]}")
    else:
        print(f"COMPROMISED: {result['events_checked']} events checked")
        for issue in result["issues"]:
            print(f"  - {issue}")
        print(f"  Final chain hash: {result.get('final_chain_hash', 'N/A')}")

    if args.warn_only:
        return EXIT_PASS
    if result["status"] in ("valid", "no_data"):
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
