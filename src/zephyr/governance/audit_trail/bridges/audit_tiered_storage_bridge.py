# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.bridges.audit_tiered_storage_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_tiered_storage_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Audit ↔ WarmHotGate 三层存储桥接.

蓝图 D-020-10 — 三层存储架构（热≤7d / 温8~90d / 冷>90d）。
集成 shared/warm_hot_gate.py + shared/contracts/core/runtime_plane_tag.py。
"""

from __future__ import annotations

import gzip
import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

_HOT_DAYS = 7
_WARM_DAYS = 90


class AuditTieredStorageBridge:
    """审计↔三层存储桥接器.

    将审计日志按时间分层:
      热 (HOT): ≤7天 — JSONL 原文，SSD 级延迟
      温 (WARM): 8~90天 — gzip 压缩 JSONL
      冷 (COLD): >90天 — 归档目录，可离线
    """

    def __init__(self, data_dir: str | Path = "data/audit-trail") -> None:
        self._data_dir = Path(data_dir)
        self._hot_dir = self._data_dir
        self._warm_dir = self._data_dir / "warm"
        self._cold_dir = self._data_dir / "cold"

    def classify_events(self, events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """按时间将事件分为三层.

        Returns:
            {"hot": [...], "warm": [...], "cold": [...]}
        """
        now = datetime.now(UTC)
        hot_cutoff = now - timedelta(days=_HOT_DAYS)
        warm_cutoff = now - timedelta(days=_WARM_DAYS)

        tiers: dict[str, list[dict[str, Any]]] = {"hot": [], "warm": [], "cold": []}

        for e in events:
            ts_str = e.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts >= hot_cutoff:
                    tiers["hot"].append(e)
                elif ts >= warm_cutoff:
                    tiers["warm"].append(e)
                else:
                    tiers["cold"].append(e)
            except (ValueError, TypeError):
                tiers["hot"].append(e)

        return tiers

    def migrate_warm(self) -> int:
        """将温层事件从 JSONL 原文迁移为 gzip 压缩.

        Returns:
            迁移的事件数量
        """
        jsonl_path = self._hot_dir / "events.jsonl"
        if not jsonl_path.exists():
            return 0

        self._warm_dir.mkdir(parents=True, exist_ok=True)

        import json

        now = datetime.now(UTC)
        hot_cutoff = now - timedelta(days=_HOT_DAYS)
        warm_cutoff = now - timedelta(days=_WARM_DAYS)

        hot_events: list[str] = []
        warm_events: list[str] = []
        migrated = 0

        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    ts_str = event.get("timestamp", "")
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts >= hot_cutoff:
                        hot_events.append(line)
                    elif ts >= warm_cutoff:
                        warm_events.append(line)
                        migrated += 1
                except (json.JSONDecodeError, ValueError, TypeError):
                    hot_events.append(line)

        if warm_events:
            warm_gz_path = self._warm_dir / f"events_{now.strftime('%Y%m%d')}.jsonl.gz"
            tmp_path = f"{warm_gz_path}.{os.getpid()}.tmp"
            try:
                with gzip.open(tmp_path, "wt", encoding="utf-8") as gz:
                    for line in warm_events:
                        gz.write(line + "\n")
                os.replace(tmp_path, warm_gz_path)
            except PermissionError:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        tmp_hot = f"{jsonl_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_hot, "w", encoding="utf-8") as f:
                for line in hot_events:
                    f.write(line + "\n")
            os.replace(tmp_hot, jsonl_path)
        except PermissionError:
            try:
                os.remove(tmp_hot)
            except OSError:
                pass

        _logger.info("TieredStorage: migrated %d events to warm layer", migrated)
        return migrated

    def get_storage_stats(self) -> dict[str, Any]:
        """获取三层存储统计.

        Returns:
            {"hot_size_mb": float, "warm_size_mb": float, "cold_size_mb": float, "hot_events": int}
        """
        stats: dict[str, Any] = {
            "hot_size_mb": 0.0,
            "warm_size_mb": 0.0,
            "cold_size_mb": 0.0,
            "hot_events": 0,
        }

        hot_jsonl = self._hot_dir / "events.jsonl"
        if hot_jsonl.exists():
            stats["hot_size_mb"] = round(hot_jsonl.stat().st_size / (1024 * 1024), 2)
            with open(hot_jsonl, encoding="utf-8") as f:
                stats["hot_events"] = sum(1 for line in f if line.strip())

        if self._warm_dir.exists():
            warm_size = sum(f.stat().st_size for f in self._warm_dir.rglob("*") if f.is_file())
            stats["warm_size_mb"] = round(warm_size / (1024 * 1024), 2)

        if self._cold_dir.exists():
            cold_size = sum(f.stat().st_size for f in self._cold_dir.rglob("*") if f.is_file())
            stats["cold_size_mb"] = round(cold_size / (1024 * 1024), 2)

        return stats
