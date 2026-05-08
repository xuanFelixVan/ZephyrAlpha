"""MOD-INF-026 §16 — 跨会话并发模型。

ConcurrentScanner：无锁并发扫描——Glide Window + SHA256 重试 + 锁感知跳过。
scan_batch：ThreadPoolExecutor 并发批量扫描。
merge_scans：多 Scanner 产出合并策略。
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from zephyr.asset_inventory.models import RawFileEntry, ScanResult


class ConcurrentScanner:

    GLIDE_WINDOW_SEC = 60
    SHA_RETRY_COUNT = 3
    SHA_RETRY_DELAY_MS = 200

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._lock_dir = project_root / ".ailocks"

    def _is_locked(self, path: Path) -> bool:
        try:
            rel = path.relative_to(self._root)
            sanitized = str(rel).replace("\\", "_").replace("/", "_")
            lock_dir = self._lock_dir / f"{sanitized}.lock"
            return lock_dir.exists()
        except ValueError:
            return False

    def scan_file(self, path: Path) -> Optional[RawFileEntry]:
        if self._is_locked(path):
            return None

        age_sec = time.time() - path.stat().st_mtime
        if age_sec < self.GLIDE_WINDOW_SEC:
            return self._scan_with_retry(path)

        return self._scan_normal(path)

    def _scan_normal(self, path: Path) -> Optional[RawFileEntry]:
        import hashlib
        try:
            st = path.stat()
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            rel_path = str(path.relative_to(self._root))
            return RawFileEntry(
                relative_path=rel_path,
                absolute_path=str(path),
                file_name=path.name,
                extension=path.suffix,
                size_bytes=st.st_size,
                mtime_utc=datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
                ctime_utc=datetime.fromtimestamp(st.st_ctime, tz=timezone.utc),
                sha256=sha,
            )
        except (OSError, PermissionError):
            return None

    def _scan_with_retry(self, path: Path) -> Optional[RawFileEntry]:
        import hashlib
        for _ in range(self.SHA_RETRY_COUNT):
            entry = self._scan_normal(path)
            if entry and self._verify_sha(path, entry.sha256):
                return entry
            time.sleep(self.SHA_RETRY_DELAY_MS / 1000)
        return None

    def _verify_sha(self, path: Path, expected: str) -> bool:
        import hashlib
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest() == expected
        except (OSError, PermissionError):
            return False

    DEFAULT_MAX_WORKERS = 4

    def scan_batch(
        self,
        paths: list[Path],
        max_workers: Optional[int] = None,
    ) -> list[RawFileEntry]:
        workers = max_workers or self.DEFAULT_MAX_WORKERS
        results: list[RawFileEntry] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_to_path = {
                pool.submit(self.scan_file, p): p for p in paths
            }
            for future in as_completed(future_to_path):
                try:
                    entry = future.result()
                    if entry is not None:
                        results.append(entry)
                except Exception:
                    pass
        return results


def merge_scans(scan_a: ScanResult, scan_b: ScanResult) -> ScanResult:
    merged: dict[str, RawFileEntry] = {}

    for e in scan_a.entries:
        merged[e.relative_path] = e

    for e in scan_b.entries:
        if e.relative_path not in merged:
            merged[e.relative_path] = e
            continue

        existing = merged[e.relative_path]
        if existing.sha256 != e.sha256:
            if e.mtime_utc > existing.mtime_utc:
                merged[e.relative_path] = e

    entries = sorted(merged.values(), key=lambda x: x.relative_path)

    return ScanResult(
        scan_id=f"MERGE-{scan_a.scan_id}+{scan_b.scan_id}",
        scanned_at=min(scan_a.scanned_at, scan_b.scanned_at),
        completed_at=max(scan_a.completed_at, scan_b.completed_at),
        total_files=len(entries),
        total_size_bytes=sum(e.size_bytes for e in entries),
        entries=entries,
    )
