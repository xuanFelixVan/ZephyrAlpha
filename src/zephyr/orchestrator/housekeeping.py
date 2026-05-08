"""文件卫生保洁管理器（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃目录清理。"""

from __future__ import annotations

class HousekeepingManager:
    TEMP_PATTERNS: list[str] = ["_temp*", "_check*", "_phase_*", "*.tmp", "*.bak"]

    def scan_temp_files(self) -> list[str]:
        return []

    def should_clean(self, filename: str) -> bool:
        return any(filename.startswith(p.replace("*", "").rstrip("*")) for p in self.TEMP_PATTERNS)
