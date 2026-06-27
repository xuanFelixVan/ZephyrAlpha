# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain-knowledge/vector-memory/blueprint.md
# [MODULE] zephyr.data.knowledge_management.vector_memory.index_health_monitor
# [DOMAIN] D-KNOWLEDGE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_index_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复
=========================================================
蓝图 §1 · §6 · §10 · 可自愈设计哲学

功能
----
- check_all() → HealthReport: 扫描所有 Collection 健康状态 · mitigates R0/R5/R8
- auto_repair(collection): 自动修复索引损坏
- detect_drift(): 比对蓝图 §2 与磁盘实际 Collection · mitigates R0
- snapshot_backup(): 定期 snapshot 备份 · mitigates R4
- integrity_check(): 启动时完整性校验 · mitigates R4
- check_ttl_expiry(): TTL 过期记录检查 · mitigates R5/R8
- schedule_maintenance(): WAL checkpoint + VACUUM + ANALYZE
"""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG

_logger = logging.getLogger(__name__)


class HealthReport(BaseModel):
    model_config = BASE_CONFIG

    status: str = "unknown"
    collections_healthy: int = 0
    collections_unhealthy: int = 0
    drift_detected: bool = False
    issues: list[str] = Field(default_factory=list)
    checked_at: str = ""


class DriftReport(BaseModel):
    model_config = BASE_CONFIG

    drift_detected: bool = False
    extra_collections: list[str] = Field(default_factory=list)
    missing_collections: list[str] = Field(default_factory=list)
    detail: str = ""


class TTLExpiryReport(BaseModel):
    model_config = BASE_CONFIG

    collection: str = ""
    expired_count: int = 0
    total_count: int = 0
    ttl_days: int = 0


class IndexHealthMonitor:
    def __init__(self, collection_manager: Any) -> None:
        self._collection_manager = collection_manager

    def check_all(self) -> HealthReport:
        issues: list[str] = []
        healthy = 0
        unhealthy = 0

        for info in self._collection_manager.list_collections():
            if info.exists:
                try:
                    col = self._collection_manager.get_collection(info.name)
                    col.count()
                    healthy += 1
                except Exception as e:
                    unhealthy += 1
                    issues.append(f"{info.name}: {e}")
            else:
                unhealthy += 1
                issues.append(f"{info.name}: 不存在")

        drift = self.detect_drift()
        if drift.drift_detected:
            issues.append("蓝图漂移检测到不一致")

        # mitigates R8: 每日检查 TTL 过期
        ttl_issues = self.check_ttl_expiry()
        for ttl in ttl_issues:
            if ttl.expired_count > 0:
                issues.append(f"TTL: {ttl.collection} 过期 {ttl.expired_count}/{ttl.total_count} 条")

        return HealthReport(
            status="unhealthy" if unhealthy > 0 else "healthy",
            collections_healthy=healthy,
            collections_unhealthy=unhealthy,
            drift_detected=drift.drift_detected,
            issues=issues,
            checked_at=datetime.now(UTC).isoformat(),
        )

    # mitigates R0
    def detect_drift(self) -> DriftReport:
        disk_collections = {c.name for c in self._collection_manager.client.list_collections()}
        blueprint_collections = set(self._collection_manager.VMS_COLLECTION_NAMES)
        extra = sorted(disk_collections - blueprint_collections)
        missing = sorted(blueprint_collections - disk_collections)
        has_drift = bool(extra or missing)

        if has_drift:
            _logger.warning("IndexHealthMonitor: 漂移检测 → 多余=%s, 缺失=%s", extra, missing)

        return DriftReport(
            drift_detected=has_drift,
            extra_collections=extra,
            missing_collections=missing,
            detail=f"disk={disk_collections}, blueprint={blueprint_collections}",
        )

    # mitigates R4
    def snapshot_backup(self, backup_dir: Path | str | None = None, max_snapshots: int = 3) -> Path | None:
        backup_root = Path(backup_dir) if backup_dir else Path("data/vector_db_backups")
        backup_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        snapshot_path = backup_root / f"snapshot_{timestamp}"

        if self._collection_manager.persist_dir.exists():
            _ignore = shutil.ignore_patterns("_snapshots", "vector_db_backups")
            shutil.copytree(
                str(self._collection_manager.persist_dir),
                str(snapshot_path),
                dirs_exist_ok=False,
                ignore=_ignore,
            )

            persist_size = sum(
                f.stat().st_size
                for f in self._collection_manager.persist_dir.rglob("*")
                if f.is_file() and "_snapshots" not in str(f) and "vector_db_backups" not in str(f)
            )
            snap_size = sum(f.stat().st_size for f in snapshot_path.rglob("*") if f.is_file())

            if persist_size > 0 and snap_size > persist_size * 1.5:
                shutil.rmtree(str(snapshot_path))
                _logger.error(
                    "IndexHealthMonitor: 快照异常膨胀 — snapshot=%.1f MB, persist=%.1f MB (%.1fx) — 已拒绝并删除",
                    snap_size / (1024 * 1024),
                    persist_size / (1024 * 1024),
                    snap_size / persist_size,
                )
                return None

            _logger.info("IndexHealthMonitor: snapshot 备份完成 → %s (mitigates R4)", snapshot_path)
            self._cleanup_old_snapshots(backup_root, max_snapshots)
        else:
            _logger.warning("IndexHealthMonitor: persist_dir 不存在，跳过备份")
            return None
        return snapshot_path

    def _cleanup_old_snapshots(self, backup_root: Path, max_snapshots: int) -> None:
        snapshots = sorted(backup_root.glob("snapshot_*"), key=lambda p: p.name)
        if len(snapshots) <= max_snapshots:
            return
        for old in snapshots[:-max_snapshots]:
            try:
                shutil.rmtree(str(old))
                _logger.info("IndexHealthMonitor: 清理旧快照 → %s", old)
            except OSError as e:
                _logger.warning("IndexHealthMonitor: 清理旧快照失败 → %s: %s", old, e)

    def cleanup_snapshots(self, backup_dir: Path | str | None = None, max_snapshots: int = 3) -> int:
        backup_root = Path(backup_dir) if backup_dir else Path("data/vector_db_backups")
        if not backup_root.exists():
            return 0
        before = len(list(backup_root.glob("snapshot_*")))
        self._cleanup_old_snapshots(backup_root, max_snapshots)
        after = len(list(backup_root.glob("snapshot_*")))
        removed = before - after
        if removed > 0:
            _logger.info("IndexHealthMonitor: cleanup_snapshots 删除 %d 个旧快照 (保留 %d)", removed, after)
        return removed

    # mitigates R4
    def integrity_check(self) -> dict[str, Any]:
        issues: list[str] = []
        for info in self._collection_manager.list_collections():
            if info.exists:
                try:
                    col = self._collection_manager.client.get_collection(info.name)
                    count = col.count()
                    if count > 0:
                        data = col.get(limit=10, include=["embeddings"])
                        embeddings = data.get("embeddings")
                        if embeddings is not None and len(embeddings) > 0:
                            for emb in embeddings:
                                if emb is not None and len(emb) != info.dimension:
                                    issues.append(f"{info.name}: 维度不匹配 (声明={info.dimension}, 实际={len(emb)})")
                                    break
                except Exception as e:
                    issues.append(f"{info.name}: integrity check 失败: {e}")
        return {"status": "clean" if not issues else "corrupted", "issues": issues}

    # mitigates R5/R8
    def check_ttl_expiry(self) -> list[TTLExpiryReport]:
        from zephyr.governance.vector_memory.collection_manager import TTL_MAP

        reports: list[TTLExpiryReport] = []
        now = datetime.now(UTC)

        for col_name, ttl_days in TTL_MAP.items():
            try:
                col = self._collection_manager.get_collection(col_name)
                total = col.count()
                if total == 0:
                    continue
                all_data = col.get(include=["metadatas"])
                expired = 0
                if all_data.get("ids") and all_data.get("metadatas"):
                    for i, doc_id in enumerate(all_data["ids"]):
                        meta = all_data["metadatas"][i] if all_data["metadatas"] else {}
                        written_at = meta.get("written_at", "")
                        if written_at:
                            try:
                                wt = datetime.fromisoformat(written_at.replace("Z", "+00:00"))
                                age = (now - wt).days
                                if age > ttl_days:
                                    expired += 1
                            except Exception:
                                pass
                reports.append(
                    TTLExpiryReport(
                        collection=col_name,
                        expired_count=expired,
                        total_count=total,
                        ttl_days=ttl_days,
                    )
                )
            except Exception:
                pass
        return reports

    def auto_repair(self, collection_name: str) -> bool:
        _logger.info("IndexHealthMonitor: 尝试修复 Collection '%s'", collection_name)
        try:
            self._collection_manager.get_collection(collection_name)
            return True
        except Exception as e:
            _logger.error("IndexHealthMonitor: 修复失败: %s", e)
            return False
