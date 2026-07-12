# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers.hotspot_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/observability/test_hotspot_tracker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_hotspot_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class HotspotEntry:
    file: str
    function: str = ""
    change_count_90d: int = 0
    duplicate_count_90d: int = 0
    last_changed: str = ""
    is_hot: bool = False


class HotspotTracker:
    """热点追踪——90天滑动窗口."""

    _WINDOW_DAYS: int = 90
    _HOT_THRESHOLD: int = 5

    def __init__(self) -> None:
        self._changes: dict[str, list[str]] = defaultdict(list)
        self._duplicates: dict[str, list[tuple[str, int]]] = defaultdict(list)

    # ── 公共 API ──────────────────────────────────────────────

    def record_change(self, file_path: str, function: str = "") -> None:
        """记录一次变更."""
        now = datetime.now(UTC).isoformat()
        self._changes[file_path].append(now)

    def record_duplicate(self, file_path: str, dup_id: str, confidence: int = 0) -> None:
        """记录一次重复发现."""
        self._duplicates[file_path].append((dup_id, confidence))

    def get_hotspots(self) -> list[HotspotEntry]:
        """获取当前热点文件列表."""
        cutoff = (datetime.now(UTC) - timedelta(days=self._WINDOW_DAYS)).isoformat()
        hotspots: list[HotspotEntry] = []

        for file_path, timestamps in self._changes.items():
            recent = [t for t in timestamps if t >= cutoff]
            dup_count = len(self._duplicates.get(file_path, []))

            if len(recent) >= self._HOT_THRESHOLD or dup_count >= self._HOT_THRESHOLD:
                hotspots.append(
                    HotspotEntry(
                        file=file_path,
                        change_count_90d=len(recent),
                        duplicate_count_90d=dup_count,
                        last_changed=recent[-1] if recent else "",
                        is_hot=True,
                    )
                )

        hotspots.sort(key=lambda h: h.change_count_90d + h.duplicate_count_90d, reverse=True)
        return hotspots[:10]

    def generate_preheat_list(self, project_files: list[str]) -> list[str]:
        """新项目预热清单——标记已有重复历史的文件."""
        known_hot_files = {h.file for h in self.get_hotspots()}
        return [
            f
            for f in project_files
            if f in known_hot_files or any(kw in f.lower() for kw in ["util", "helper", "common", "base"])
        ]

    def get_90d_summary(self) -> dict[str, Any]:
        """90天摘要."""
        hotspots = self.get_hotspots()
        total_changes = sum(h.change_count_90d for h in hotspots)
        total_duplicates = sum(h.duplicate_count_90d for h in hotspots)
        return {
            "window_days": self._WINDOW_DAYS,
            "total_hotspots": len(hotspots),
            "total_changes": total_changes,
            "total_duplicates": total_duplicates,
            "top_hotspots": [h.file for h in hotspots[:5]],
        }
