# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.reconciler
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
# [A_module] module_id=MOD-INF_reconciler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ReconciliationEngine — MOD-INF-026 L4 注册表 vs 磁盘对账引擎

蓝图 §3.4：比对新扫描结果 vs unified-asset-index.yaml -> 检测三类偏移
（孤儿/幽灵/漂移），产出 reconciliation-report.md。
"""

import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.infrastructure.asset_inventory.models import (
    ClassificationResult,
    ClassifiedAsset,
    DriftEntry,
    DriftType,
    GhostEntry,
    RawFileEntry,
    ReconciliationReport,
    RenameEvent,
    ScanResult,
    UnifiedAssetIndex,
)

logger = logging.getLogger(__name__)


class Reconciler:
    """对账引擎——对比磁盘实际 vs 注册表记录（蓝图 §3.4）。"""

    def __init__(
        self,
        orphan_tolerance_hours: int = 24,
        ghost_max_age_days: int = 30,
        root: Path | None = None,
    ) -> None:
        self.orphan_tolerance_hours = orphan_tolerance_hours
        self.ghost_max_age_days = ghost_max_age_days
        self.root = root or REPO_ROOT

    def _compare_scan_vs_index(
        self,
        scan_sha: dict[str, RawFileEntry],
        class_by_path: dict[str, ClassifiedAsset],
        index_assets: dict[str, ClassifiedAsset],
        now: datetime,
    ) -> tuple[int, list[ClassifiedAsset], list[DriftEntry]]:
        """对比扫描结果与注册表索引，返回 (matched, orphans, drifts)。"""
        matched = 0
        orphans: list[ClassifiedAsset] = []
        drifts: list[DriftEntry] = []
        for path, entry in scan_sha.items():
            cls = class_by_path.get(path)
            mtime_dt = entry.mtime_utc.replace(tzinfo=UTC)
            if path not in index_assets:
                if mtime_dt.tzinfo is None:
                    mtime_dt = mtime_dt.replace(tzinfo=UTC)
                delta = now - mtime_dt
                if delta < timedelta(hours=self.orphan_tolerance_hours):
                    matched += 1
                    continue
                orphans.append(
                    cls
                    or ClassifiedAsset(
                        relative_path=path,
                        asset_type=cls.asset_type if cls else AssetType.UNKNOWN,
                        size_bytes=entry.size_bytes,
                        mtime_utc=entry.mtime_utc,
                        sha256=entry.sha256,
                    )
                )
                continue
            idx = index_assets[path]
            drift_types: list[DriftType] = []
            if idx.sha256 != entry.sha256:
                drift_types.append(DriftType.SHA256)
            if idx.size_bytes != entry.size_bytes:
                drift_types.append(DriftType.SIZE)
            if drift_types:
                drifts.append(
                    DriftEntry(
                        relative_path=path,
                        registered_sha256=idx.sha256,
                        disk_sha256=entry.sha256,
                        drift_types=drift_types,
                        registered_size=idx.size_bytes,
                        disk_size=entry.size_bytes,
                        registered_mtime=idx.mtime_utc,
                        disk_mtime=entry.mtime_utc,
                    )
                )
            else:
                matched += 1
        return matched, orphans, drifts

    def _detect_ghosts(
        self,
        index_assets: dict[str, ClassifiedAsset],
        scan_sha: dict[str, RawFileEntry],
        existing_index: UnifiedAssetIndex | None,
        now: datetime,
    ) -> list[GhostEntry]:
        """检测幽灵条目：注册表中存在但磁盘上不存在的资产。"""
        ghosts: list[GhostEntry] = []
        for path, idx in index_assets.items():
            if path not in scan_sha:
                p = self.root / path
                ghost_days = 0.0
                if existing_index and existing_index.last_reconciliation_at:
                    ghost_days = (now - existing_index.last_reconciliation_at).total_seconds() / 86400.0
                ghosts.append(
                    GhostEntry(
                        registry_id="unified-asset-index",
                        registry_path=path,
                        registered_type=idx.asset_type if hasattr(idx, "asset_type") else AssetType.UNKNOWN,
                        cached_sha256=idx.sha256 if hasattr(idx, "sha256") else None,
                        last_known_mtime=idx.mtime_utc if hasattr(idx, "mtime_utc") else None,
                        ghost_since=now,
                        days_ghost=round(ghost_days, 1),
                        candidates_for_cleanup=ghost_days > self.ghost_max_age_days,
                    )
                )
        return ghosts

    def reconcile(
        self,
        scan_result: ScanResult,
        classified: ClassificationResult,
        existing_index: UnifiedAssetIndex | None = None,
        *,
        dry_run: bool = True,
    ) -> ReconciliationReport:
        report_id = _generate_report_id()
        now = datetime.now(UTC)
        logger.info("开始对账: %s (dry_run=%s)", report_id, dry_run)

        scan_sha: dict[str, RawFileEntry] = {e.relative_path: e for e in scan_result.entries}
        class_by_path: dict[str, ClassifiedAsset] = {}
        for a in classified.assets:
            class_by_path[a.relative_path] = a

        index_assets: dict[str, ClassifiedAsset] = {}
        if existing_index:
            for a in existing_index.assets:
                index_assets[a.relative_path] = a

        matched, orphans, drifts = self._compare_scan_vs_index(
            scan_sha, class_by_path, index_assets, now
        )
        ghosts = self._detect_ghosts(index_assets, scan_sha, existing_index, now)

        total = matched + len(orphans) + len(ghosts) + len(drifts)
        orphan_before = (len(orphans) / total * 100) if total else 0.0

        renames, orphans, ghosts = _detect_renames(orphans, ghosts)

        orphan_after = (len(orphans) / total * 100) if total else 0.0

        summary = (
            f"对账完成——一致: {matched} | 孤儿: {len(orphans)} | "
            f"幽灵: {len(ghosts)} | 漂移: {len(drifts)} | "
            f"重命名: {len(renames)}"
        )

        logger.info(summary)

        return ReconciliationReport(
            report_id=report_id,
            scan_id=scan_result.scan_id,
            dry_run=dry_run,
            matched=matched,
            orphans=orphans,
            ghosts=ghosts,
            drifts=drifts,
            renames=renames,
            registries_checked=1,
            auto_fixed_count=len(renames),
            orphan_rate_before=round(orphan_before, 1),
            orphan_rate_after=round(orphan_after, 1),
            summary_text=summary,
        )

    def save(self, report: ReconciliationReport, output_path: Path | None = None) -> Path:
        reports_dir = self.root / "data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        target = output_path or (reports_dir / "reconciliation-report.md")

        lines = _format_report_md(report)
        content = "\n".join(lines)

        tmp = f"{target}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, target)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

        logger.info("对账报告已写入: %s", target)
        return Path(target)


def _detect_renames(
    orphans: list[ClassifiedAsset], ghosts: list[GhostEntry]
) -> tuple[list[RenameEvent], list[ClassifiedAsset], list[GhostEntry]]:
    """通过 sha256 匹配孤儿与幽灵，检测重命名事件，返回 (renames, remaining_orphans, remaining_ghosts)。"""
    renames: list[RenameEvent] = []
    ghost_by_sha: dict[str, GhostEntry] = {}
    for g in ghosts:
        if g.cached_sha256:
            ghost_by_sha[g.cached_sha256] = g
    for o in orphans[:]:
        if o.sha256 in ghost_by_sha:
            gh = ghost_by_sha[o.sha256]
            renames.append(
                RenameEvent(
                    old_path=gh.registry_path,
                    new_path=o.relative_path,
                    sha256=o.sha256,
                    confidence=0.95,
                )
            )
            orphans.remove(o)
            ghosts.remove(gh)
    return renames, orphans, ghosts


def _generate_report_id() -> str:
    now = datetime.now(UTC)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"RECON-{now.strftime('%Y%m%d')}-{seq}"


def _format_report_md(report: ReconciliationReport) -> list[str]:
    lines: list[str] = []
    lines.append(f"# 资产对账报告 — {report.report_id}")
    lines.append(f"**生成时间** {report.reconciled_at.isoformat()}")
    lines.append(f"**扫描 ID**   {report.scan_id}")
    lines.append(f"**模式**       {'DRY-RUN（无修改）' if report.dry_run else 'APPLY（已应用）'}")
    lines.append("")

    lines.append("## 总览")
    lines.append("| 项目 | 数量 |")
    lines.append("|------|------|")
    lines.append(f"| 一致 (MATCHED) | {report.matched} |")
    lines.append(f"| 孤儿 (ORPHAN) | {len(report.orphans)} |")
    lines.append(f"| 幽灵 (GHOST) | {len(report.ghosts)} |")
    lines.append(f"| 漂移 (DRIFT) | {len(report.drifts)} |")
    lines.append(f"| 重命名 (RENAME) | {len(report.renames)} |")
    lines.append(f"| 检查注册表 | {report.registries_checked} |")
    lines.append(f"| 孤儿率 (前) | {report.orphan_rate_before}% |")
    lines.append(f"| 孤儿率 (后) | {report.orphan_rate_after}% |")
    lines.append("")

    if report.renames:
        lines.append("## 检测到重命名")
        for r in report.renames:
            lines.append(f"- `{r.old_path}` -> `{r.new_path}` (SHA256: `{r.sha256[:12]}...`, conf={r.confidence:.0%})")
        lines.append("")

    if report.orphans:
        lines.append(f"## 孤儿资产 ({len(report.orphans)})")
        lines.append("磁盘存在，索引中无记录：")
        for o in report.orphans:
            lines.append(f"- `{o.relative_path}` ({o.asset_type}, {o.size_bytes:,}B, mtime={o.mtime_utc})")
        lines.append("")

    if report.ghosts:
        lines.append(f"## 幽灵引用 ({len(report.ghosts)})")
        lines.append("索引中有记录，磁盘上文件不存在：")
        for g in report.ghosts:
            clean = " [建议清理]" if g.candidates_for_cleanup else ""
            lines.append(f"- `{g.registry_path}` ({g.registered_type}, 幽灵 {g.days_ghost:.0f}d){clean}")
        lines.append("")

    if report.drifts:
        lines.append(f"## 数据漂移 ({len(report.drifts)})")
        lines.append("索引信息与磁盘实际状态不一致：")
        for d in report.drifts:
            types = ", ".join(t.value for t in d.drift_types)
            lines.append(f"- `{d.relative_path}`: {types}")
        lines.append("")

    return lines


def main() -> None:
    Reconciler().main()


if __name__ == "__main__":
    main()
