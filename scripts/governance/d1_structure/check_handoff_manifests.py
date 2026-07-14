# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_handoff_manifests.py | §
# [MODULE] scripts.governance.check_handoff_manifests
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
#!/usr/bin/env python
"""
check_handoff_manifests.py — AI Session Handoff Manifest 完整性校验.

依据: MOD-MASTER_BLUEPRINT §22.3 CT-SESSION-handoff-001
验证 .trae/session_state/ 目录下所有 CT-*_progress.yaml 是否存在且不超过 30 天未更新.

用法:
    python scripts/governance/check_handoff_manifests.py           # 标准检查
    python scripts/governance/check_handoff_manifests.py --json    # JSON 输出
    python scripts/governance/check_handoff_manifests.py --warn-only  # 不因 YELLOW 退出

exit: 0=CLEAN, 1=WARNINGS, 2=ERRORS
"""

from __future__ import annotations

__manifest__ = """
args: []
description: check_handoff_manifests.py — AI Session Handoff Manifest 完整性校验.
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

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

PROJECT_ROOT = REPO_ROOT
SESSION_STATE_DIR = PROJECT_ROOT / ".trae" / "session_state"

REQUIRED_MANIFEST_FIELDS = [
    "ct_id",
    "last_session_date",
    "completion_percent",
    "completed_items",
    "remaining_items",
    "known_issues",
    "files_touched",
    "next_session_instructions",
]

STALE_DAYS_WARN = 14
STALE_DAYS_CRITICAL = 30

UTC = timezone.utc


def list_manifests() -> list[Path]:
    """list_manifests implementation."""
    if not SESSION_STATE_DIR.is_dir():
        return []
    return sorted(SESSION_STATE_DIR.glob("*_progress.yaml"))


def parse_manifest(manifest_path: Path) -> dict | None:
    """parse_manifest implementation."""
    import yaml

    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def validate_manifest_fields(data: dict, manifest_path: Path) -> list[str]:
    """Validate target against rules and report findings."""
    missing: list[str] = []
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in data or data[field] is None:
            missing.append(field)
    return missing


def check_manifest_staleness(data: dict, manifest_path: Path) -> dict:
    """Check compliance and report findings."""
    last_date_str = data.get("last_session_date", "")
    if not last_date_str:
        return {"status": "FAIL", "reason": "missing last_session_date"}

    try:
        last_date = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
        if last_date.tzinfo is None:
            last_date = last_date.replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return {"status": "FAIL", "reason": f"invalid date format: {last_date_str}"}

    now = datetime.now(UTC)
    age_days = (now - last_date).days

    if age_days > STALE_DAYS_CRITICAL:
        return {
            "status": "FAIL",
            "reason": f"stale {age_days}d (> {STALE_DAYS_CRITICAL}d critical)",
            "age_days": age_days,
        }
    if age_days > STALE_DAYS_WARN:
        return {"status": "WARN", "reason": f"stale {age_days}d (> {STALE_DAYS_WARN}d warning)", "age_days": age_days}
    return {"status": "OK", "reason": f"fresh ({age_days}d)", "age_days": age_days}


def check_manifest(manifest_path: Path) -> dict:
    """Check compliance and report findings."""
    rel_path = (
        str(manifest_path.relative_to(PROJECT_ROOT))
        if manifest_path.is_relative_to(PROJECT_ROOT)
        else str(manifest_path)
    )

    result: dict = {
        "manifest": rel_path,
        "field_check": "OK",
        "staleness_check": "OK",
        "status": "OK",
        "details": [],
    }

    if not manifest_path.exists():
        result.update(
            {"status": "FAIL", "field_check": "FAIL", "staleness_check": "FAIL", "details": ["file not found"]}
        )
        return result

    data = parse_manifest(manifest_path)
    if data is None:
        result.update({"status": "FAIL", "field_check": "FAIL", "staleness_check": "FAIL", "details": ["invalid YAML"]})
        return result

    ct_id = data.get("ct_id", "unknown")
    result["ct_id"] = ct_id
    result["completion_percent"] = data.get("completion_percent", 0)

    missing_fields = validate_manifest_fields(data, manifest_path)
    if missing_fields:
        result["field_check"] = "FAIL"
        result["details"].append(f"missing fields: {', '.join(missing_fields)}")

    staleness = check_manifest_staleness(data, manifest_path)
    if staleness["status"] != "OK":
        result["staleness_check"] = staleness["status"]
        result["details"].append(staleness["reason"])

    if result["field_check"] == "FAIL" or result["staleness_check"] == "FAIL":
        result["status"] = "FAIL"
    elif result["staleness_check"] == "WARN":
        result["status"] = "WARN"

    return result


def get_expected_contracts() -> list[str]:
    """get_expected_contracts implementation."""
    try:
        from zephyr.orchestrator.contracts.contract_registry import ContractRegistry

        cr = ContractRegistry()
        return [c.contract_id for c in cr.list_all()]
    except Exception:
        return []


def check_missing_manifests() -> list[dict]:
    """Check compliance and report findings."""
    existing_manifests = list_manifests()
    existing_ct_ids: set[str] = set()
    for mf in existing_manifests:
        data = parse_manifest(mf)
        if data and data.get("ct_id"):
            existing_ct_ids.add(data["ct_id"])

    expected = get_expected_contracts()
    results: list[dict] = []
    for ct_id in expected:
        if ct_id not in existing_ct_ids:
            try:
                from zephyr.orchestrator.contracts.contract_registry import AIReadOnlyHint, ContractRegistry

                cr = ContractRegistry()
                contract = cr.get(ct_id)
                hint = contract.ai_read_only_hint if contract else None

                if hint in (AIReadOnlyHint.DO_NOT_CALL, None):
                    continue
            except Exception:
                pass

            results.append(
                {
                    "ct_id": ct_id,
                    "status": "WARN",
                    "reason": "no handoff manifest — AI session 上下文不可恢复",
                }
            )

    return results


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    use_json = "--json" in sys.argv
    warn_only = "--warn-only" in sys.argv

    results: list[dict] = []

    if not SESSION_STATE_DIR.is_dir():
        if use_json:
            print(
                json.dumps(
                    {"status": "FAIL", "reason": "session_state directory missing"}, indent=2, ensure_ascii=False
                )
            )
        else:
            print("FAIL: .trae/session_state/ 目录不存在")
        return EXIT_ERROR

    manifests = list_manifests()
    if not manifests:
        missing = check_missing_manifests()
        if missing:
            results.extend(missing)
        if use_json:
            print(
                json.dumps(
                    {"status": "OK", "manifests": 0, "message": "暂无 handoff manifest — 所有 CT-* 均未开始施工"},
                    indent=2,
                    ensure_ascii=False,
                )
            )
        else:
            print("OK: 暂无 handoff manifest（所有 CT-* 均未开始施工或处于 DO_NOT_CALL）")
        return EXIT_PASS

    ok_count = 0
    warn_count = 0
    fail_count = 0

    for mf in manifests:
        r = check_manifest(mf)
        results.append(r)
        if r["status"] == "FAIL":
            fail_count += 1
        elif r["status"] == "WARN":
            warn_count += 1
        else:
            ok_count += 1

    missing = check_missing_manifests()
    results.extend(missing)
    warn_count += len(missing)

    if use_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            if r.get("manifest"):
                icon = {"OK": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(r["status"], "[??]")
                ct = r.get("ct_id", "?")
                pct = r.get("completion_percent", "?")
                print(f"  {icon} {r['manifest']}  ct={ct}  {pct}%  {', '.join(r.get('details', []))}")
            else:
                print(f"  [WARN] {r['ct_id']}: {r['reason']}")

        print(f"\n{ok_count} OK, {warn_count} WARN, {fail_count} FAIL")

    if fail_count > 0:
        return EXIT_ERROR
    if warn_count > 0 and not warn_only:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
