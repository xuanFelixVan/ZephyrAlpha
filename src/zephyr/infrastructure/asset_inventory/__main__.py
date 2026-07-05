# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.__main__
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Asset Inventory CLI — MOD-INF-026 蓝图 §31

用法:
    python -m zephyr.data.asset_inventory scan       # 全量文件系统扫描
    python -m zephyr.data.asset_inventory classify    # 资产自动分类
    python -m zephyr.data.asset_inventory reconcile   # 注册表 vs 磁盘对账
    python -m zephyr.data.asset_inventory dashboard   # 健康仪表盘
    python -m zephyr.data.asset_inventory check       # Gate 检查 (exit 0=GREEN, 1=RED)
    python -m zephyr.data.asset_inventory bootstrap   # 从零自举 (scan→classify→reconcile→dashboard)
    python -m zephyr.data.asset_inventory clean       # 清理过期产物

共享标志: --dry-run, --output json/yaml/text, --verbose, --help
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.infrastructure.asset_inventory.classifier import Classifier
from zephyr.infrastructure.asset_inventory.dashboard import Dashboard
from zephyr.infrastructure.asset_inventory.index_generator import IndexGenerator
from zephyr.infrastructure.asset_inventory.reconciler import Reconciler
from zephyr.infrastructure.asset_inventory.scanner import Scanner
from zephyr.infrastructure.asset_inventory.telemetry import get_telemetry

logger = logging.getLogger(__name__)



def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.asset_inventory",
        description="ZephyrAlpha 资产盘点系统 (MOD-INF-026)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="全量文件系统扫描")
    p_scan.add_argument("--incremental", action="store_true")
    p_scan.add_argument("--dry-run", action="store_true")

    p_cls = sub.add_parser("classify", help="资产自动分类")
    p_cls.add_argument("--dry-run", action="store_true")

    p_rec = sub.add_parser("reconcile", help="注册表 vs 磁盘对账")
    p_rec.add_argument("--dry-run", action="store_true", default=True)
    p_rec.add_argument("--apply", action="store_true")
    p_rec.add_argument("--auto-fix", action="store_true")

    p_dash = sub.add_parser("dashboard", help="健康仪表盘")
    p_dash.add_argument("--show-trends", action="store_true")

    p_chk = sub.add_parser("check", help="Gate 检查")
    p_chk.add_argument("--json", action="store_true")

    p_boot = sub.add_parser("bootstrap", help="从零自举")
    p_boot.add_argument("--from-scratch", action="store_true")

    p_clean = sub.add_parser("clean", help="清理过期产物")
    p_clean.add_argument("--dry-run", action="store_true", default=True)
    p_clean.add_argument("--apply", action="store_true")

    p_deps = sub.add_parser("deps", help="构建资产依赖图")

    p_reg = sub.add_parser("registries", help="列出/解析所有注册表")

    for p in [p_scan, p_cls, p_rec, p_dash, p_chk, p_boot, p_clean, p_deps, p_reg]:
        p.add_argument("--output", choices=["json", "yaml", "text"], default="text")
        p.add_argument("--verbose", "-v", action="store_true")

    return parser.parse_args()


def _load_scan() -> str | None:
    p = REPO_ROOT / "data" / "scans" / "raw-asset-scan.json"
    return str(p) if p.exists() else None


def _load_classified() -> str | None:
    p = REPO_ROOT / "data" / "classified" / "classified-assets.json"
    return str(p) if p.exists() else None


def _cmd_scan(args: argparse.Namespace) -> int:
    s = Scanner()
    if args.dry_run:
        from collections import deque

        count = 0
        for d in s.directories:
            ad = REPO_ROOT / d
            if ad.is_dir():
                q = deque([ad])
                while q:
                    entry = q.popleft()
                    try:
                        for child in entry.iterdir():
                            if child.is_symlink() or child.name in s.excludes:
                                continue
                            if child.is_dir():
                                q.append(child)
                            elif child.is_file():
                                count += 1
                    except PermissionError:
                        pass
        print(f"[DRY-RUN] 将扫描约 {count} 个文件")
        return 0

    result = s.scan(incremental=args.incremental)
    out = s.save(result)
    print(f"  SCAN    {result.scan_id}")
    print(f"  FILES   {result.total_files}")
    print(f"  SIZE    {result.total_size_bytes:,} bytes")
    print(f"  TIME    {result.duration_seconds:.1f}s")
    print(f"  OUTPUT  {out}")
    return 0


def _cmd_classify(args: argparse.Namespace) -> int:
    scan_path = _load_scan()
    if not scan_path:
        print("错误: 扫描文件不存在——先运行 scan", file=sys.stderr)
        print("  python -m zephyr.data.asset_inventory scan", file=sys.stderr)
        return 2

    import json as _json

    data = _json.loads(Path(scan_path).read_text(encoding="utf-8"))
    from zephyr.infrastructure.asset_inventory.models import RawFileEntry, ScanResult

    entries = [RawFileEntry(**e) for e in data["entries"]]
    scan = ScanResult(**{**data, "entries": entries})

    c = Classifier()
    if args.dry_run:
        print(f"[DRY-RUN] 将分类 {scan.total_files} 个文件")
        return 0

    result = c.classify(scan)

    out_dir = REPO_ROOT / "data" / "classified"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "classified-assets.json"
    payload = result.model_dump(mode="json")
    tmp = f"{out}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(_json.dumps(payload, ensure_ascii=False, indent=2))
    os.replace(tmp, out)

    print(f"  CLASSIFY  {result.classification_id}")
    print(f"  TOTAL     {result.total_classified}")
    print(f"  UNKNOWN   {result.unknown_count} ({result.unknown_pct}%)")
    print(f"  BY TYPE   {result.by_type}")
    print(f"  OUTPUT    {out}")
    return 0


def _cmd_reconcile(args: argparse.Namespace) -> int:
    scan_path = _load_scan()
    klass_path = _load_classified()
    if not scan_path or not klass_path:
        print("错误: 扫描或分类文件不存在——先运行 scan + classify", file=sys.stderr)
        return 2

    import json as _json

    sdata = _json.loads(Path(scan_path).read_text(encoding="utf-8"))
    cdata = _json.loads(Path(klass_path).read_text(encoding="utf-8"))

    from zephyr.infrastructure.asset_inventory.models import (
        ClassificationResult,
        ClassifiedAsset,
        RawFileEntry,
        ScanResult,
        UnifiedAssetIndex,
    )

    entries = [RawFileEntry(**e) for e in sdata["entries"]]
    scan = ScanResult(**{**sdata, "entries": entries})
    assets = [ClassifiedAsset(**a) for a in cdata.get("assets", [])]
    classified = ClassificationResult(**{**cdata, "assets": assets})

    idx_path = REPO_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"
    existing = None
    if idx_path.exists():
        import yaml

        raw = yaml.safe_load(idx_path.read_text(encoding="utf-8"))
        existing = UnifiedAssetIndex(**raw)

    r = Reconciler()
    dry = not args.apply
    report = r.reconcile(scan, classified, existing_index=existing, dry_run=dry)

    if dry:
        _print_dry_run_preview(report, scan_path or "")
        return 0

    auto_fixed = 0
    if args.auto_fix:
        auto_fixed = _auto_fix_orphans(report.orphans)

    report = r.reconcile(scan, classified, existing_index=existing, dry_run=False)
    out = r.save(report)

    print(f"  RECONCILE  {report.report_id}")
    print(f"  MATCHED    {report.matched}")
    print(f"  ORPHANS    {len(report.orphans)}")
    print(f"  GHOSTS     {len(report.ghosts)}")
    print(f"  DRIFTS     {len(report.drifts)}")
    print(f"  RENAMES    {len(report.renames)}")
    if auto_fixed:
        print(f"  AUTO-FIX   {auto_fixed} 个孤儿通过 scaffold 自动注册")
    print(f"  OUTPUT     {out}")
    return 0


def _print_dry_run_preview(report, scan_path: str) -> None:
    orphans_by_ext: dict[str, int] = {}
    auto_fixable = 0
    manual_orphans = 0
    for o in report.orphans:
        ext = Path(o.relative_path).suffix
        orphans_by_ext[ext] = orphans_by_ext.get(ext, 0) + 1
        if ext in (".py",):
            auto_fixable += 1
        else:
            manual_orphans += 1

    registries_str = f"{report.registries_checked}/{report.registries_checked + report.registries_skipped}"
    if report.skipped_registry_ids:
        registries_str += f" (跳过 {report.registries_skipped} 个损坏: {', '.join(report.skipped_registry_ids[:3])})"

    total = report.matched + len(report.orphans) + len(report.ghosts) + len(report.drifts)
    orphan_pct = (len(report.orphans) / total * 100) if total else 0.0

    lines: list[str] = []
    lines.append("")
    lines.append("[DRY-RUN] \u5bf9\u8d26\u9884\u6f14 \u2014 \u4e0d\u4f1a\u4fee\u6539\u4efb\u4f55\u6587\u4ef6")
    lines.append("\u2501" * 40)
    lines.append(f"  \u57fa\u4e8e\u626b\u63cf: {report.scan_id}")
    lines.append(f"  \u6bd4\u5bf9\u6ce8\u518c\u8868: {registries_str}")
    lines.append("")
    lines.append("  \u8d44\u4ea7\u72b6\u6001:")
    lines.append(f"    \u4e00\u81f4 (MATCHED):    {report.matched}")
    lines.append(
        f"    \u5b64\u513f (ORPHAN):     {len(report.orphans)}   \u2190 \u78c1\u76d8\u5b58\u5728\uff0c\u6ce8\u518c\u8868\u65e0"
    )
    lines.append(
        f"    \u5e7d\u7075 (GHOST):      {len(report.ghosts)}   \u2190 \u6ce8\u518c\u8868\u6709\uff0c\u78c1\u76d8\u4e0d\u5b58\u5728"
    )
    lines.append(
        f"    \u6f02\u79fb (DRIFT):      {len(report.drifts)}   \u2190 \u6ce8\u518c\u4fe1\u606f/\u78c1\u76d8\u4e0d\u5339\u914d"
    )
    if report.renames:
        lines.append(
            f"    \u91cd\u547d\u540d (RENAME):    {len(report.renames)}   \u2190 SHA256 \u4ea4\u53c9\u5339\u914d\u68c0\u6d4b"
        )
    lines.append("")
    if auto_fixable > 0:
        lines.append("  \u81ea\u52a8\u4fee\u590d\u9884\u89c8:")
        for ext, count in sorted(orphans_by_ext.items()):
            if ext == ".py":
                lines.append(f"    \u5b64\u513f .py \u2192 scaffold register:  {count} \u4e2a")
            elif ext == ".yaml":
                lines.append(f"    \u5b64\u513f .yaml \u2192 scaffold gate:    {count} \u4e2a")
        if manual_orphans:
            lines.append(
                f"    \u5269\u4f59\u9700\u4eba\u5de5\u5904\u7406\u7684\u5b64\u513f:            {manual_orphans} \u4e2a ({', '.join(f'.{e}' for e in orphans_by_ext if e not in ('.py', '.yaml'))})"
            )
        lines.append("")
        lines.append("  \u5982\u679c\u6267\u884c reconcile --apply --auto-fix:")
        lines.append(f"    scaffold \u81ea\u52a8\u6ce8\u518c {auto_fixable} \u4e2a\u6587\u4ef6")
        est_after = max(0.0, orphan_pct - (auto_fixable / total * 100) if total else 0.0)
        lines.append(
            f"    \u5b64\u513f\u7387: {orphan_pct:.1f}% \u2192 {est_after:.1f}%  (\u2193{orphan_pct - est_after:.1f}pp)"
        )
    lines.append("\u2501" * 40)
    lines.append("")

    print("\n".join(lines))


def _auto_fix_orphans(orphans: list) -> int:
    import subprocess

    fixed = 0
    scaffold_script = str(REPO_ROOT / "scripts" / "scaffold.py")

    for o in orphans:
        ext = Path(o.relative_path).suffix
        if ext != ".py":
            continue

        rel = o.relative_path
        if rel.startswith("src/zephyr/"):
            parts = rel.replace("src/zephyr/", "").split("/")
            if len(parts) >= 2:
                pkg = parts[0]
                name = parts[-1].replace(".py", "")
                try:
                    subprocess.run(
                        ["python", scaffold_script, "module", pkg, name, "--desc", f"auto-fix orphan: {rel}"],
                        capture_output=True,
                        timeout=30,
                        cwd=str(REPO_ROOT),
                    )
                    fixed += 1
                except Exception as e:
                    logger.warning("_auto_fix_orphans: scaffold module register failed for %s (%s: %s)", rel, type(e).__name__, e, exc_info=True)
        elif rel.startswith("scripts/"):
            script_rel = rel.replace("scripts/", "").replace(".py", "")
            try:
                subprocess.run(
                    ["python", scaffold_script, "script", script_rel, "--desc", f"auto-fix orphan: {rel}"],
                    capture_output=True,
                    timeout=30,
                    cwd=str(REPO_ROOT),
                )
                fixed += 1
            except Exception as e:
                logger.warning("_auto_fix_orphans: scaffold script register failed for %s (%s: %s)", rel, type(e).__name__, e, exc_info=True)

    return fixed


def _cmd_dashboard(args: argparse.Namespace) -> int:
    idx_p = REPO_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"
    if not idx_p.exists():
        print("错误: 索引文件不存在——先运行 scan → classify → reconcile", file=sys.stderr)
        return 2

    import yaml

    raw = yaml.safe_load(idx_p.read_text(encoding="utf-8"))
    from zephyr.infrastructure.asset_inventory.models import UnifiedAssetIndex

    index = UnifiedAssetIndex(**raw)

    d = Dashboard()
    dash = d.generate(index)
    out = d.save(dash)
    d.print_summary(dash)
    print(f"  OUTPUT {out}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    idx_p = REPO_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"
    result: dict[str, object] = {}

    if not idx_p.exists():
        result = {"health_score": "N/A", "gate": "YELLOW", "reason": "索引不存在——运行 bootstrap"}
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
            return 1
        print("YELLOW: 索引不存在")
        return 1

    import yaml

    index = yaml.safe_load(idx_p.read_text(encoding="utf-8"))
    health = index.get("health_score", "N/A")
    orphan = index.get("orphan_rate_pct", 0.0)
    ghost = index.get("ghost_rate_pct", 0.0)
    total = index.get("total_assets", 0)

    gate = "GREEN"
    reason = ""

    if health in ("D", "F"):
        gate = "RED"
        reason = f"健康评分 {health}"
    elif orphan > 5.0:
        gate = "RED"
        reason = f"孤儿率 {orphan:.1f}% 超过 5%"
    elif orphan > 2.0:
        gate = "YELLOW"
        reason = f"孤儿率 {orphan:.1f}% 超过 2%"
    elif total == 0:
        gate = "YELLOW"
        reason = "资产数为 0"

    result = {
        "health_score": health,
        "orphan_rate_pct": orphan,
        "ghost_rate_pct": ghost,
        "total_assets": total,
        "gate": gate,
        "reason": reason or "OK",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"{gate}: {reason or 'OK'} (health={health}, orphan={orphan:.1f}%)")

    return 0 if gate == "GREEN" else 1


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    """scan → classify → index → reconcile → dashboard"""
    print("开始自举重建...")

    s = Scanner()
    result = s.scan()
    s.save(result)
    print(f"  [1/5] SCAN      {result.total_files} files, {result.duration_seconds:.1f}s")

    c = Classifier()
    classified = c.classify(result)
    out_dir = REPO_ROOT / "data" / "classified"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "classified-assets.json"
    payload = classified.model_dump(mode="json")
    tmp = f"{out}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))
    os.replace(tmp, out)
    print(f"  [2/5] CLASSIFY  {classified.total_classified} assets, {classified.unknown_pct:.1f}% unknown")

    ig = IndexGenerator()
    index = ig.generate(classified)
    ig.save(index)
    print(f"  [3/5] INDEX     health={index.health_score}")

    r = Reconciler()
    report = r.reconcile(result, classified, existing_index=index, dry_run=False)
    r.save(report)
    print(f"  [4/5] RECONCILE matched={report.matched} orphans={len(report.orphans)} ghosts={len(report.ghosts)}")

    d = Dashboard()
    dash = d.generate(index)
    d.save(dash)
    d.print_summary(dash)
    print("  [5/5] DASHBOARD")

    t = get_telemetry()
    t.inc("bootstrap_completed")
    t.set_gauge("last_bootstrap_assets", float(index.total_assets))
    t.push_to_facade()

    return 0


def _cmd_clean(args: argparse.Namespace) -> int:
    dry = not args.apply
    cleanup_dirs = [
        REPO_ROOT / "data" / "scans",
        REPO_ROOT / "data" / "classified",
        REPO_ROOT / "data" / "reports",
    ]

    total = 0
    for d in cleanup_dirs:
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if f.is_file() and f.suffix in (".json", ".md"):
                total += 1
                if not dry:
                    f.unlink(missing_ok=True)

    if dry:
        print(f"[DRY-RUN] 将删除 {total} 个过期产物")
        print("  运行 --apply 确认删除")
    else:
        print(f"已清理 {total} 个产物")
    return 0


def _cmd_deps(args: argparse.Namespace) -> int:
    scan_path = _load_scan()
    if not scan_path:
        print("错误: 扫描文件不存在——先运行 scan", file=sys.stderr)
        return 2

    import json as _json

    sdata = _json.loads(Path(scan_path).read_text(encoding="utf-8"))
    entries = sdata.get("entries", sdata.get("assets", []))

    from zephyr.infrastructure.asset_inventory.dependency import build_dependency_graph

    graph = build_dependency_graph(entries, REPO_ROOT)

    print("  DEPENDENCY GRAPH")
    print(f"  files          {graph.total_files}")
    print(f"  edges          {graph.total_edges}")
    print(f"  nodes          {len(graph.nodes)}")
    print(f"  top-depended   {graph.most_depended_upon[:5]}")
    if graph.circular_dependencies:
        print(f"  cycles         {len(graph.circular_dependencies)} cycles detected!")
        for cycle in graph.circular_dependencies[:3]:
            print(f"    → {' → '.join(cycle)}")
    if graph.orphan_imports:
        print(f"  orphan-imports {len(graph.orphan_imports)} unresolved")
        for imp in graph.orphan_imports[:5]:
            print(f"    → {imp}")

    print("  （依赖图统一由 generate_project_depgraph.py 产出到 depgraph (PostgreSQL)，不再产 JSON）")
    return 0


def _cmd_registries(args: argparse.Namespace) -> int:
    from zephyr.infrastructure.asset_inventory.registry_adapter import RegistryManager

    mgr = RegistryManager(REPO_ROOT)
    entries, skipped = mgr.load_all()

    print("  REGISTRIES")
    print(f"  files found    {len(mgr.discover_registry_files())}")
    print(f"  entries parsed {len(entries)}")
    print(f"  skipped        {len(skipped)}")
    if skipped:
        for s in skipped[:5]:
            print(f"    → {s}")

    reg_dist: dict[str, int] = {}
    for e in entries:
        reg_dist[e.registry_id] = reg_dist.get(e.registry_id, 0) + 1
    for rid, count in sorted(reg_dist.items()):
        print(f"    {rid:30s}  {count} entries")
    return 0


_COMMANDS = {
    "scan": _cmd_scan,
    "classify": _cmd_classify,
    "reconcile": _cmd_reconcile,
    "dashboard": _cmd_dashboard,
    "check": _cmd_check,
    "bootstrap": _cmd_bootstrap,
    "clean": _cmd_clean,
    "deps": _cmd_deps,
    "registries": _cmd_registries,
}

_EXIT_CODES = {
    0: "SUCCESS",
    1: "GATE_RED",
    2: "SCAN_ERROR",
    3: "CONFIG_ERROR",
    4: "REGISTRY_CORRUPT",
    5: "TIMEOUT",
}


def main() -> None:
    args = _parse_args()
    handler = _COMMANDS.get(args.command or "")
    if not handler:
        print(f"未知命令: {args.command}", file=sys.stderr)
        sys.exit(3)

    try:
        code = handler(args)
    except KeyboardInterrupt:
        code = 5
    except Exception as exc:
        logger.exception("命令 %s 异常", args.command, exc_info=True)
        print(f"ERROR: {exc}", file=sys.stderr)
        code = 2

    if code != 0:
        label = _EXIT_CODES.get(code, f"EXIT_{code}")
        if args.verbose:
            print(f"退出: {label} ({code})")

    sys.exit(code)


if __name__ == "__main__":
    main()