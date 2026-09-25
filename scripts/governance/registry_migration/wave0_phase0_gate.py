# [MODULE] scripts.governance.registry_migration.wave0_phase0_gate
# [DOMAIN] D_GOVERNANCE
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [STARTUP] manual
# [MATURITY] production
# [MODIFY-GUARD] 新建 2026-09-24 st-wm1-wave0-20260924（W-M1 波0⑤验收通道）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单册扫描失败不拖垮全景（SCAN-FAIL 行继续）；DB 异常折入非零退出码
# [TESTS] tests/governance/test_registry_ledger_baseline.py（引擎层红蓝）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: W-M1 验收/运维通道按需调用 runner（人工+CI+监控事件触发），非 cron 非 daemon 非常驻
# [DEPENDENCIES] zephyr.governance.registry_ledger.baseline (scan/import/publish/reconcile)
# [CONSUMERS] 运维/验收通道（W-M1 波0⑤Phase 0 对账门 + Phase 1 双轨 24h 对账报告制）
# [INVARIANTS] 只读扫描默认零 DB 写；--import/--publish/--reconcile 显式才写；
#   对账报告 JSON 落 .runtime/registry_ledger/（禁 .runtime 根直写）；
#   Phase 0 PASS 机械判据=七册（或指定册）reconcile 全部 zero_unexplained_drift=True
# [TESTS] tests/governance/test_registry_ledger_baseline.py（引擎层红蓝）
"""W-M1 波0 Phase 0 基线对账门 CLI。

用法：
  python scripts/governance/registry_migration/wave0_phase0_gate.py scan
  python scripts/governance/registry_migration/wave0_phase0_gate.py import --dry-run
  python scripts/governance/registry_migration/wave0_phase0_gate.py import
  python scripts/governance/registry_migration/wave0_phase0_gate.py publish
  python scripts/governance/registry_migration/wave0_phase0_gate.py reconcile --out report.json
  python scripts/governance/registry_migration/wave0_phase0_gate.py gate   # import+publish+reconcile 全链门
指定单册：--registry <physical_path 子串>；默认 P0 七册（09 号文 A-1 名单）。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  canonical 常量，禁本地重定义（SSOT）

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from zephyr.governance.registry_ledger.baseline import (  # noqa: E402
    import_baseline,
    load_roor_index,
    p0_physical_paths,
    publish_snapshot,
    reconcile_registry,
    scan_registry_file,
)

REPORT_DIR = REPO_ROOT / ".runtime" / "registry_ledger"


def _select(paths: list, needle: str | None) -> list[str]:
    if not needle:
        return paths
    return [p for p in paths if needle in p] or [_p for _p in paths if needle in _p]


def cmd_scan(args: argparse.Namespace) -> int:
    roor = load_roor_index(REPO_ROOT)
    paths = _select(p0_physical_paths(REPO_ROOT), args.registry)
    for p in paths:
        try:
            scan = scan_registry_file(REPO_ROOT, p)
        except Exception as exc:  # noqa: BLE001 — 单册扫描失败不拖垮全景
            print(f"[SCAN-FAIL] {p}: {exc}")
            continue
        print(
            f"{scan['registry_id']:<22} entries={scan['entries_total']:<6} "
            f"passthrough={scan['passthrough_total']:<4} primary={scan['primary_family']} "
            f"mode={scan['identity_mode']:<19} maintenance={scan['maintenance'][:20]}"
        )
    print(f"ROOR indexed paths: {len(roor)}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    paths = _select(p0_physical_paths(REPO_ROOT), args.registry)
    reports = []
    for p in paths:
        t0 = time.monotonic()
        rep = import_baseline(REPO_ROOT, p, dry_run=args.dry_run, session_id=args.session)
        rep["elapsed_s"] = round(time.monotonic() - t0, 2)
        reports.append(rep)
        print(
            f"[{'DRY' if args.dry_run else 'IMPORT'}] {rep['registry_id']:<22} "
            f"total={rep['scan']['entries_total']:<6} imported={rep['entries_imported']:<6} "
            f"skipped={rep['entries_skipped_existing']:<6} passthrough={rep['scan']['passthrough_total']:<4} "
            f"{rep['elapsed_s']}s"
        )
    _write_report("import", reports, args)
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    paths = _select(p0_physical_paths(REPO_ROOT), args.registry)
    head = _git_head()
    reports = []
    for p in paths:
        scan = scan_registry_file(REPO_ROOT, p)
        rep = publish_snapshot(scan["registry_id"], git_commit_ref=head, session_id=args.session)
        reports.append(rep)
        tag = "NOOP" if rep["noop"] else f"v{rep['snapshot_version']}"
        print(f"[PUBLISH {tag:>4}] {rep['registry_id']:<22} entries={rep['entry_count']}")
    _write_report("publish", reports, args)
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    paths = _select(p0_physical_paths(REPO_ROOT), args.registry)
    reports = []
    all_pass = True
    for p in paths:
        rep = reconcile_registry(REPO_ROOT, p, session_id=args.session)
        reports.append(rep)
        ok = rep["zero_unexplained_drift"]
        all_pass = all_pass and ok
        print(
            f"[{'PASS' if ok else 'DRIFT'}] {rep['registry_id']:<22} "
            f"yaml={rep['yaml_entries']:<6} pg={rep['pg_entries']:<6} "
            f"backfilled={rep['backfilled']:<4} mismatch={rep['content_mismatch']:<4} "
            f"pg_only={rep['pg_only']:<4} clean={rep['clean_match']}"
        )
    verdict = "Phase 0 PASS (zero unexplained drift)" if all_pass else "Phase 0 FAIL (drift present)"
    print(verdict)
    _write_report("reconcile", {"verdict": verdict, "all_pass": all_pass, "registries": reports}, args)
    return 0 if all_pass else 2


def cmd_gate(args: argparse.Namespace) -> int:
    """全链门：import（幂等）→ publish（幂等）→ reconcile → 机械判据。"""
    ns = argparse.Namespace(session=args.session, registry=args.registry, out=args.out)
    rc = cmd_import(argparse.Namespace(session=args.session, registry=args.registry, dry_run=False, out=args.out))
    if rc:
        return rc
    cmd_publish(ns)
    return cmd_reconcile(ns)


def _git_head() -> str | None:
    import subprocess  # noqa: PLC0415

    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip()[:40]
    except Exception:  # noqa: BLE001 — git 不可用不阻断发布（字段可空）
        return None


def _write_report(kind: str, payload: object, args: argparse.Namespace) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = Path(args.out) if args.out else REPORT_DIR / f"{kind}_{stamp}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8", newline="\n")
    print(f"report → {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description="W-M1 wave0 Phase 0 baseline gate")
    ap.add_argument("command", choices=["scan", "import", "publish", "reconcile", "gate"])
    ap.add_argument("--registry", default=None, help="physical_path 子串筛选（默认 P0 七册）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--session", default="st-wm1-wave0-20260924")
    ap.add_argument("--out", default=None, help="报告输出路径（默认 .runtime/registry_ledger/）")
    args = ap.parse_args()
    return {
        "scan": cmd_scan,
        "import": cmd_import,
        "publish": cmd_publish,
        "reconcile": cmd_reconcile,
        "gate": cmd_gate,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
