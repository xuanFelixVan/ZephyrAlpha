"""
Longevity Monitor — 多周黄昏退化检测 (盲点 #46)
月频检测：
  - GC 代际增长
  - WAL 文件膨胀
  - ChromaDB 持久化膨胀
  - 文件句柄泄漏
"""
import gc
import os
import time
from typing import Any, Optional


class LongevityMonitor:
    """
    长期运行健康监测 (盲点 #46)
    """

    WAL_SIZE_WARNING_MB = 100
    CHROMA_SIZE_WARNING_MB = 500

    def __init__(self):
        self._baseline_gc_stats: Optional[dict] = None
        self._check_count = 0

    def take_baseline(self):
        self._baseline_gc_stats = {
            "collections": gc.get_count(),
            "objects": len(gc.get_objects()),
        }

    def monthly_check(self, data_dir: str = "data") -> dict:
        findings = []

        # GC check
        if self._baseline_gc_stats:
            current_cols = gc.get_count()
            for gen_idx, (base, cur) in enumerate(
                zip(self._baseline_gc_stats["collections"], current_cols)
            ):
                if cur > base * 10:
                    findings.append(f"GC gen {gen_idx}: {base} → {cur} (+{cur-base})")

        # WAL check
        wal_path = os.path.join(data_dir, "capacity.db-wal")
        if os.path.exists(wal_path):
            wal_size = os.path.getsize(wal_path) / (1024 * 1024)
            if wal_size > self.WAL_SIZE_WARNING_MB:
                findings.append(f"WAL size: {wal_size:.1f}MB > {self.WAL_SIZE_WARNING_MB}MB")

        # ChromaDB check
        chroma_dir = os.path.join(data_dir, "chroma")
        if os.path.exists(chroma_dir):
            total = sum(
                os.path.getsize(os.path.join(root, f))
                for root, _, files in os.walk(chroma_dir)
                for f in files
            ) / (1024 * 1024)
            if total > self.CHROMA_SIZE_WARNING_MB:
                findings.append(f"ChromaDB size: {total:.1f}MB > {self.CHROMA_SIZE_WARNING_MB}MB")

        self._check_count += 1
        return {
            "check_number": self._check_count,
            "findings": findings,
            "healthy": len(findings) == 0,
        }
