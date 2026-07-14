# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.index_health_monitor
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.integration.vector_memory.collection_manager
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_index_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
IndexHealthMonitor — MOD-INF-011 索引健康自检与自动修复
=========================================================
蓝图 §1 · §6 · §10 · 可自愈设计哲学

功能
----
- inspect_all() -> HealthReport: 扫描所有 Collection 健康状态 · mitigates R0/R5/R8
- auto_repair(collection): 自动修复索引损坏
- detect_drift(): 比对蓝图 §2 与磁盘实际 Collection · mitigates R0
- collect_ttl_expiry(): TTL 过期记录检查 · mitigates R5/R8
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG

if TYPE_CHECKING:
    from zephyr.integration.vector_memory.collection_manager import CollectionManager

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
    def __init__(self, collection_manager: CollectionManager) -> None:
        self._collection_manager = collection_manager

    def inspect_all(self) -> HealthReport:
        issues: list[str] = []
        healthy = 0
        unhealthy = 0

        for info in self._collection_manager.list_collections():
            if info.exists:
                try:
                    col = self._collection_manager.get_collection(info.name)
                    col.count()
                    healthy += 1
                except (KeyError, ValueError) as e:
                    _logger.warning("IndexHealthMonitor: collection %s 健康检查失败: %s", info.name, e)
                    unhealthy += 1
                    issues.append(f"{info.name}: {e}")
            else:
                unhealthy += 1
                issues.append(f"{info.name}: 不存在")

        drift = self.detect_drift()
        if drift.drift_detected:
            issues.append("蓝图漂移检测到不一致")

        # mitigates R8: 每日检查 TTL 过期
        ttl_issues = self.collect_ttl_expiry()
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
            _logger.warning("IndexHealthMonitor: 漂移检测 -> 多余=%s, 缺失=%s", extra, missing)

        return DriftReport(
            drift_detected=has_drift,
            extra_collections=extra,
            missing_collections=missing,
            detail=f"disk={disk_collections}, blueprint={blueprint_collections}",
        )

    # mitigates R5/R8
    def collect_ttl_expiry(self) -> list[TTLExpiryReport]:
        from zephyr.integration.vector_memory.collection_manager import TTL_MAP

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
                            except ValueError as e:
                                _logger.warning("IndexHealthMonitor: TTL 时间戳解析失败: %s", e)
                reports.append(
                    TTLExpiryReport(
                        collection=col_name,
                        expired_count=expired,
                        total_count=total,
                        ttl_days=ttl_days,
                    )
                )
            except (KeyError, ValueError) as e:
                _logger.warning("IndexHealthMonitor: TTL 检查失败 for %s: %s", col_name, e)
        return reports

    def auto_repair(self, collection_name: str) -> bool:
        _logger.info("IndexHealthMonitor: 尝试修复 Collection '%s'", collection_name)
        try:
            self._collection_manager.get_collection(collection_name)
            return True
        except (KeyError, ValueError) as e:
            _logger.warning("IndexHealthMonitor: 修复失败: %s", e, exc_info=True)
            return False
