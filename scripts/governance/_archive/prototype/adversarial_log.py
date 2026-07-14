# [BLUEPRINT] MOD-INF-005 | scripts/governance/adversarial_log.py | §
# [MODULE] scripts.governance.adversarial_log
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
"""红白对抗闭环记录——攻击→根源分析→修复→回归验证→知识注入全链路追踪

用法:
    python scripts/governance/adversarial_log.py --list         # 列出所有对抗记录
    python scripts/governance/adversarial_log.py --json         # JSON输出（AI消费）
    python scripts/governance/adversarial_log.py --add          # 交互式添加记录
    python scripts/governance/adversarial_log.py --summary      # 摘要报告
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

_LOG_PATH = PROJECT_ROOT / "data" / "adversarial_log.jsonl"
_TS_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _load_entries() -> list[dict]:
    """_load_entries implementation."""
    if not _LOG_PATH.exists():
        return []
    entries: list[dict] = []
    with open(_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _append_entry(entry: dict) -> None:
    """_append_entry implementation."""
    entry["logged_at"] = datetime.now(UTC).strftime(_TS_FORMAT)
    tmp = f"{_LOG_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, _LOG_PATH)
    except PermissionError:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _add_entry(
    attack_id: str, subsystem: str, vector: str, result: str, root_cause: str, fix: str, verified: bool, notes: str
) -> dict:
    """_add_entry implementation."""
    entry = {
        "attack_id": attack_id,
        "subsystem": subsystem,
        "attack_vector": vector,
        "result": result,
        "root_cause": root_cause,
        "fix_applied": fix,
        "verified": verified,
        "notes": notes,
    }
    _append_entry(entry)
    logger.info("recorded: %s (%s) → %s", attack_id, subsystem, result)
    return entry


def _summary_report(entries: list[dict]) -> dict:
    """_summary_report implementation."""
    total = len(entries)
    passed = sum(1 for e in entries if e.get("result") == "PASS")
    fixed = sum(1 for e in entries if e.get("verified", False))
    by_subsystem: dict[str, dict] = {}
    for e in entries:
        sub = e.get("subsystem", "unknown")
        by_subsystem.setdefault(sub, {"total": 0, "pass": 0, "fixed": 0, "critical": 0})
        by_subsystem[sub]["total"] += 1
        if e.get("result") == "PASS":
            by_subsystem[sub]["pass"] += 1
        if e.get("verified", False):
            by_subsystem[sub]["fixed"] += 1
        if e.get("result") == "CRITICAL":
            by_subsystem[sub]["critical"] += 1

    return {
        "total_attacks": total,
        "pass_rate": f"{passed}/{total}" if total else "N/A",
        "fix_rate": f"{fixed}/{total}" if total else "N/A",
        "by_subsystem": by_subsystem,
        "latest": entries[-1] if entries else None,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="红白对抗闭环记录")
    parser.add_argument("--list", action="store_true", help="列出所有记录")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--summary", action="store_true", help="摘要报告")
    parser.add_argument("--add", action="store_true", help="交互式添加")
    args = parser.parse_args()

    entries = _load_entries()

    if args.json:
        report = _summary_report(entries)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if args.summary:
        report = _summary_report(entries)
        print(f"\n{'=' * 60}")
        print("  红白对抗闭环摘要")
        print(f"{'=' * 60}")
        print(f"  总攻击次数:  {report['total_attacks']}")
        print(f"  通过率:      {report['pass_rate']}")
        print(f"  修复率:      {report['fix_rate']}")
        print(f"{'=' * 60}\n")
        for sub, stats in report["by_subsystem"].items():
            print(
                f"  [{sub}] {stats['total']} attacks | {stats['pass']}P | {stats['fixed']}FIXED | {stats['critical']}CRIT"
            )
        print()
        return

    if args.add:
        print("红白对抗记录添加（Ctrl+C 取消）\n")
        try:
            attack_id = input("  攻击ID: ").strip()
            subsystem = input("  子系统: ").strip()
            vector = input("  攻击向量: ").strip()
            result = input("  结果 (PASS/FAIL/CRITICAL): ").strip()
            root_cause = input("  根源分析: ").strip()
            fix = input("  修复措施: ").strip()
            verified = input("  已验证? (y/n): ").strip().lower() == "y"
            notes = input("  备注: ").strip()
            entry = _add_entry(attack_id, subsystem, vector, result, root_cause, fix, verified, notes)
            print(f"\n已记录: {entry['attack_id']}")
        except (KeyboardInterrupt, EOFError):
            print("\n取消")
        return

    if args.list or True:
        if not entries:
            print("暂无对抗记录。使用 --add 添加第一条。")
            return
        print(f"\n{'=' * 80}")
        print(f"  红白对抗记录 ({len(entries)} 条)")
        print(f"{'=' * 80}")
        for i, e in enumerate(entries[-20:], 1):
            status = "✅" if e.get("result") == "PASS" else ("❌" if e.get("result") == "FAIL" else "⚠️")
            fixed = " [FIXED]" if e.get("verified") else ""
            print(
                f"  {status} {e.get('attack_id', '?')} | {e.get('subsystem', '?')} | {e.get('attack_vector', '?')[:40]}{fixed}"
            )
        if len(entries) > 20:
            print(f"  ... showing last 20 of {len(entries)} entries")
        print()


if __name__ == "__main__":
    main()
